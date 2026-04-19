from django.urls import path
import quantserver.views as vi

urlpatterns = [
    path("get-public-key/", vi.getUserPublicKey),
    path("post-email", vi.postEmail),
    path("register-user", vi.registerUser),
    path("check-uniqueness/", vi.checkForUniqueness),
    path("get-inbox", vi.returnInbox),
    path("clear-inbox", vi.clearInbox),
    # ETSI GS QKD 014 endpoints
    path("api/v1/keys/<str:target_ID>/enc_keys", vi.getEncKeys),
    path("api/v1/keys/<str:source_ID>/dec_keys", vi.getDecKeys),
]
