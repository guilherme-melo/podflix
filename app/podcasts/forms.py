from django import forms
from .models import Episodes

MODELS = (
    ('bm25', 'BM25'),
    ('semantic', 'SEMANTIC'),
)

EPISODES = Episodes.objects

class RecommendationForm(forms.Form):
    model = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'options'}),
        choices=MODELS,
        label="Escolha um modelo"
    )
    episode = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'options'}),
        choices=[(episode.id, episode.title) for episode in EPISODES.all()],
        label="Escolha um podcast"
    )


