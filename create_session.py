import instaloader
import browser_cookie3


USERNAME = "asisten.pr2"


L = instaloader.Instaloader()

# ambil cookies browser
cookiejar = browser_cookie3.firefox(
    domain_name=".instagram.com"
)

# inject ke session Instaloader
L.context._session.cookies.update(
    cookiejar
)

# test login
login_user = L.test_login()

if not login_user:

    raise Exception(
        "Instagram cookies invalid"
    )

print(
    f"✅ Login sebagai: "
    f"{login_user}"
)

# set username
L.context.username = USERNAME

# save session
L.save_session_to_file(
    "data/session/instagram.session"
)

print(
    "✅ Session berhasil disimpan"
)