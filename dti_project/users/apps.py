from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "users"
    verbose_name = "Users"

    def ready(self):
        # ensure signal handlers are registered
        import users.signals  # noqa
