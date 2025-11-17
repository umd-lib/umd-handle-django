import csv
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from django.core.management.base import BaseCommand, CommandError

from umd_handle.api.models import JWTToken


class Command(BaseCommand):
    help = "Import JWT tokens from a CSV into the JWTToken model."

    def add_arguments(self, parser):
        parser.add_argument('csvfile', help='Path to CSV file to import')
        parser.add_argument('--dry-run', action='store_true', help='Validate only, do not save')

    def handle(self, *args, **options):
        csvfile = options['csvfile']
        dry_run = options['dry_run']

        try:
            f = open(csvfile, newline='', encoding='utf-8')
        except OSError as e:
            raise CommandError(f"Could not open file: {e}")

        reader = csv.DictReader(f)
        created = 0
        updated = 0
        skipped = 0
        errors = []

        for rownum, row in enumerate(reader, start=2):
            # Expected columns: id,token,description,created_at,updated_at
            token = row.get('token')
            description = row.get('description')
            created_at_raw = row.get('created_at')
            updated_at_raw = row.get('updated_at')

            if not token or not description:
                skipped += 1
                self.stdout.write(self.style.WARNING(f"Row {rownum}: missing token or description; skipping."))
                continue

            # parse datetimes if present
            def parse_ts(ts_raw):
                if not ts_raw:
                    return None
                dt = parse_datetime(ts_raw)
                if dt is None:
                    # try common format fallback
                    try:
                        dt = datetime.fromisoformat(ts_raw)
                    except Exception:
                        return None
                if timezone.is_naive(dt):
                    return timezone.make_aware(dt, timezone.get_default_timezone())
                return dt

            created_at = parse_ts(created_at_raw)
            updated_at = parse_ts(updated_at_raw)

            # Create or update matching token
            try:
                with transaction.atomic():
                    if JWTToken.objects.filter(token=token).exists():
                        obj, exists = (JWTToken.objects.get(token=token), True)
                    else:
                        obj, exists = (JWTToken(token=token), False)

                    obj.description = description

                    # Validate model fields before saving
                    try:
                        obj.full_clean()
                    except ValidationError as ve:
                        errors.append((rownum, f"Validation error: {ve.message_dict if hasattr(ve, 'message_dict') else ve.messages}"))
                        continue

                    if dry_run:
                        if exists:
                            updated += 1
                        else:
                            created += 1
                        self.stdout.write(self.style.NOTICE(f"Row {rownum} would be {'updated' if exists else 'created'}: {description}"))
                        continue

                    # Save the object (creates or updates)
                    obj.save()

                    # If timestamps were provided, set them explicitly if fields exist.
                    ts_update_fields = []
                    if created_at and hasattr(obj, 'created'):
                        obj.created = created_at
                        ts_update_fields.append('created')

                    if ts_update_fields:
                        obj.save(update_fields=ts_update_fields)

                    # Adjust modified date using QuerySet.update, to prevent
                    # "auto_now=True" from resetting it.
                    if updated_at and hasattr(obj, 'modified'):
                        JWTToken.objects.filter(id=obj.id).update(modified = updated_at)

                    if exists:
                        updated += 1
                    else:
                        created += 1

            except Exception as exc:
                errors.append((rownum, f"Unexpected error: {exc}"))

        f.close()

        # Report
        self.stdout.write(self.style.SUCCESS(f"Import finished: created={created} updated={updated} skipped={skipped} errors={len(errors)}"))
        if errors:
            self.stdout.write(self.style.ERROR("Errors (row, message):"))
            for r, msg in errors:
                self.stdout.write(self.style.ERROR(f" - {r}: {msg}"))
