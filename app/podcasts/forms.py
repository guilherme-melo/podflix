from django import forms
from .models import Episodes

RECOMMENDATION_MODELS = (
    ('semantic', 'SEMANTIC'),
)

BY_TOPIC_MODELS =(
    ('bm25', 'BM25'),
    ('semantic', 'SEMANTIC'),
    ('fusion', 'FUSION')
)

EPISODES = Episodes.objects

class RecommendationForm(forms.Form):
    model = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'options'}),
        choices=RECOMMENDATION_MODELS,
        label="Escolha um modelo"
    )
    episode = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'options'}),
        choices=[(episode.id, episode.title) for episode in EPISODES.all()],
        label="Escolha um podcast"
    )

class ByTopicForm(forms.Form):
    model = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'options'}),
        choices=BY_TOPIC_MODELS,
        label="Escolha um modelo"
    )
    topic = forms.CharField(
        initial= 'Digite um assunto...'
    )

