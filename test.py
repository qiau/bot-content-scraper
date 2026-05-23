import instaloader

from src.services.instagram_loader import L


profile = instaloader.Profile.from_username(
    L.context,
    "cristiano"
)

print(profile.username)
print(profile.biography)
print(profile.followers)
print(profile.mediacount)