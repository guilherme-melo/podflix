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

INPUT_MODELS = (
    ('title', 'TITULO'),
    ('desc', 'DESCRIÇÃO'),
    ('transcript', 'TRANSCRIÇÃO')
)

MV_MODELS = (
    ('sim', 'SIM'),
    ('nao', 'NAO'),
)

EPISODES = Episodes.objects

class RecommendationForm(forms.Form):
    model = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'options'}),
        choices=RECOMMENDATION_MODELS,
        label="Escolha um modelo"
    )
    input = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'options'}),
        choices=INPUT_MODELS,
        label="Escolha qual dado usar para a query"
    )
    mv = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'options'}),
        choices=MV_MODELS,
        label="Multi-Vector?"
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
        label="Escolha o modelo"
    )
    mv = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'options'}),
        choices=MV_MODELS,
        label="Multi-Vector?"
    )
    topic = forms.CharField(
        initial= 'Digite um assunto...'
    )

