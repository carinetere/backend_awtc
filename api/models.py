# api/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

def upload_to_user_photo(instance, filename):
    # permet de stocker les photos dans media/users/<uuid>/<filename>
    return f'users/{instance.id}/{filename}'

class Utilisateur(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=150)
    entreprise = models.CharField(max_length=255, blank=True, null=True)
    numero_tel = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to=upload_to_user_photo, blank=True, null=True)

    # champs Django à personnaliser
    USERNAME_FIELD = 'email'       # on utilise l'email pour se connecter
    REQUIRED_FIELDS = ['username', 'nom', 'prenoms']  # username est toujours requis par AbstractUser

    def __str__(self):
        return f'{self.nom} {self.prenoms} ({self.email})'
    
User = settings.AUTH_USER_MODEL

# ----------------------------
# Demande de connexion
# ----------------------------
class DemandeConnexion(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expediteur = models.ForeignKey(User, related_name='demandes_envoyees', on_delete=models.CASCADE)
    destinataire = models.ForeignKey(User, related_name='demandes_recues', on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50, blank=True, null=True)  # type / méthode

# ----------------------------
# Chat B2B
# ----------------------------
class Conversation(models.Model):
    TYPE_CHOICES = [('privee','Privée'), ('groupe','Groupe')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='privee')
    titre = models.CharField(max_length=255, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

class ConversationUser(models.Model):
    ROLE_CHOICES = [('membre','Membre'),('admin','Admin')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Conversation, related_name='participants', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='membre')
    date_entree = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50, blank=True, null=True)

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    date_envoie = models.DateTimeField(auto_now_add=True)
    date_modifie = models.DateTimeField(auto_now=True)
    lu = models.BooleanField(default=False)
    method = models.CharField(max_length=50, blank=True, null=True)

# ----------------------------
# Publication / Réseaux sociaux
# ----------------------------
class Publication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    video = models.FileField(upload_to='publications/videos/', blank=True, null=True)
    user = models.ForeignKey(User, related_name='publications', on_delete=models.CASCADE)
    method = models.CharField(max_length=50, blank=True, null=True)

class PhotoPublication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo = models.ImageField(upload_to='publications/photos/')
    post = models.ForeignKey(Publication, related_name='photos', on_delete=models.CASCADE)
    method = models.CharField(max_length=50, blank=True, null=True)

class Commentaire(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    post = models.ForeignKey(Publication, related_name='commentaires', on_delete=models.CASCADE)
    method = models.CharField(max_length=50, blank=True, null=True)

class Reply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    comment = models.ForeignKey(Commentaire, related_name='replies', on_delete=models.CASCADE)
    method = models.CharField(max_length=50, blank=True, null=True)

class LikePost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    like = models.BooleanField(default=True)
    post = models.ForeignKey(Publication, related_name='likes', on_delete=models.CASCADE)
    method = models.CharField(max_length=50, blank=True, null=True)

class LikeCommentaire(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    like = models.BooleanField(default=True)
    comment = models.ForeignKey(Commentaire, related_name='likes', on_delete=models.CASCADE)
    method = models.CharField(max_length=50, blank=True, null=True)

# ----------------------------
# Notification / Preference
# ----------------------------
class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    libelle = models.TextField()
    date_ajout = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    method = models.CharField(max_length=50, blank=True, null=True)

class Preference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    langue = models.CharField(max_length=50, blank=True, null=True)
    notification = models.BooleanField(default=True)
    user = models.OneToOneField(User, related_name='preference', on_delete=models.CASCADE)
    method = models.CharField(max_length=50, blank=True, null=True)

# ----------------------------
# Evenements / Panels
# ----------------------------
class Evenement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    libelle = models.CharField(max_length=255)
    description = models.TextField()
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    # 🔹 Localisation
    lieu = models.CharField(max_length=255, help_text="Nom du lieu ou salle (ex: Palais des Congrès)")
    adresse = models.TextField(blank=True, null=True, help_text="Adresse complète")
    ville = models.CharField(max_length=100, blank=True, null=True)
    pays = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Latitude GPS")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Longitude GPS")

    image = models.ImageField(upload_to='evenements/images/', blank=True, null=True)
    method = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.libelle} - {self.lieu or 'Lieu non défini'}"

class Stand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="stands/logos/")
    description = models.TextField(blank=True, null=True)

    method = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nom

class Panel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    libelle = models.CharField(max_length=255)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    num_salle = models.CharField(max_length=255)
    evenement = models.ForeignKey(Evenement, related_name="panels", on_delete=models.CASCADE)

    # ✅ utilisateurs qui suivent ce panel (favoris)
    favoris = models.ManyToManyField(User, through="FavoriPanel", related_name="panels_favoris")

    method = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.libelle} ({self.evenement.libelle})"


class Paneliste(models.Model):
    ROLE_CHOICES = [
        ("intervenant", "Intervenant"),
        ("moderateur", "Modérateur"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=150)
    poste = models.CharField(max_length=100, blank=True, null=True)
    entreprise = models.CharField(max_length=150, blank=True, null=True)
    photo = models.ImageField(upload_to="panelistes/photos/", blank=True, null=True)
    bibliographie = models.TextField(blank=True, null=True)

    panels = models.ManyToManyField(Panel, related_name="panelistes")

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default="intervenant")
    method = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenoms} - {self.role}"


class FavoriPanel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "panel")

    def __str__(self):
        return f"{self.user} suit {self.panel}"
    