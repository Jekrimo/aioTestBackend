# from datetime import timezone


# class User:
#     def _create_user(self, name, email, password):
#         if not email:
#             raise ValueError('Users must have an email address')
#         now = timezone.now()
#         email = self.normalize_email(email)
#         user = self.model(
#             name=name,
#             email=email,
#             password=password,
#             is_active=True,
#             last_login=now,
#             date_joined=now,
#         )
#         user.set_password(password)
#         return user

#     def create_user(self, email=None, password=None, **extra_fields):
#         return self._create_user(email, password, False, False, **extra_fields)

