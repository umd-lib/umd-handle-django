import csv
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from django.core.management.base import BaseCommand, CommandError

from umd_handle.api.models import Handle


class Command(BaseCommand):
    help = "Import handles from a CSV into the Handle model."

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

        url_validator = URLValidator(schemes=['http', 'https'])

        for rownum, row in enumerate(reader, start=2):
            # Expected columns: id,prefix,suffix,url,repo,repo_id,description,notes,created_at,updated_at
            id=row.get('id')
            prefix = row.get('prefix')
            suffix_raw = row.get('suffix')
            url = row.get('url')
            repo = row.get('repo')
            repo_id = row.get('repo_id')
            description = row.get('description') or ''
            notes = row.get('notes') or ''
            created_at_raw = row.get('created_at')
            updated_at_raw = row.get('updated_at')

            if not prefix or not suffix_raw:
                skipped += 1
                self.stdout.write(self.style.WARNING(f"Row {rownum}: missing prefix or suffix; skipping."))
                continue

            try:
                suffix = int(suffix_raw)
            except (TypeError, ValueError):
                errors.append((rownum, f"Invalid suffix: {suffix_raw}"))
                continue

            # Basic URL validation (catch totally malformed values early)
            try:
                if url:
                    url_validator(url)
            except ValidationError as e:
                errors.append((rownum, f"id={id},prefix/suffix={prefix}/{suffix}, Invalid URL '{url}': {e.messages}"))
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

            # Create or update matching prefix+suffix
            try:
                with transaction.atomic():
                    if Handle.objects.filter(prefix=prefix, suffix=suffix).exists():
                        obj, exists = (Handle.objects.get(prefix=prefix, suffix=suffix), True)
                    else:
                        obj, exists = (Handle(prefix=prefix, suffix=suffix), False)

                    obj.url = url
                    obj.repo = repo
                    obj.repo_id = repo_id
                    obj.description = description
                    obj.notes = notes

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
                        self.stdout.write(self.style.NOTICE(f"Row {rownum} would be {'updated' if exists else 'created'}: {prefix}/{suffix}"))
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
                        Handle.objects.filter(id=obj.id).update(modified = updated_at)

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
