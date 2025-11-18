# Environment Banner

## Introduction

In keeping with [SSDR policy][confluence-env-banners], an environment banner
should be displayed when running the application locally, or in the
sandbox, test, or qa Kubernetes environments, indicating the environment.

## Environment Banner Settings

This application uses the "[django-admin-notice][django-admin-notice]" package
for configuring and displaying the environment banner.

The environment banner is configured via environment variables, which are used
to provide the settings in the "src/umd_handle/settings.py" file.

The "django-admin-notice" package uses different settings than the environment
variables typically used in SSDR applications. The following table maps the
environment variables to the "django-admin-notice" settings:

| Environment variable          | django-admin-notice setting |
| ----------------------------- | --------------------------- |
| ENVIRONMENT_BANNER            | ADMIN_NOTICE_TEXT           |
| ENVIRONMENT_BANNER_FOREGROUND | ADMIN_NOTICE_TEXT_COLOR.    |
| ENVIRONMENT_BANNER_BACKGROUND | ADMIN_NOTICE_BACKGROUND.    |

* `ENVIRONMENT_BANNER` - the text to display in the banner
* `ENVIRONMENT_BANNER_FOREGROUND` - CSS color code (i.e., '#fff') for the
   foreground text
* `ENVIRONMENT_BANNER_BACKGROUND` - CSS color code (i.e., '#008000') for the
  background text

When the Django `DEBUG` setting is `True`, the "Local Environment" banner will
be displayed by default (as configured in the "settings.py" file).

When the Django `DEBUG` setting is `False`, the banner will not be displayed
`ENVIRONMENT_BANNER` environment variable is not set of empty.

---
[confluence-env-banners]: https://umd-dit.atlassian.net/wiki/spaces/LIB/pages/21431530/Create+Environment+Banners
[django-admin-notice]: https://github.com/DoctorJohn/django-admin-notice
