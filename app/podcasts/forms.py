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
        widget=forms.Select(attrs={'class': 'options'}),
        choices=RECOMMENDATION_MODELS,
        label="Escolha um modelo"
    )
    input = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'options'}),
        choices=INPUT_MODELS,
        label="Escolha qual dado usar para busca"
    )
    mv = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'options'}),
        required=False,
        label="Multi-Vector?"
    )
    episode = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'options'}),
        choices=[(episode.id, episode.title) for episode in EPISODES.all()],
        label="Escolha um podcast"
    )

class ByTopicForm(forms.Form):
    model = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'options'}),
        choices=BY_TOPIC_MODELS,
        label="Escolha o modelo"
    )
    mv = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'options'}),
        required=False,
        label="Multi-Vector?"
    )
    #texto inicial desaparece ao clicar no campo
    topic = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'options', 'placeholder': 'Digite o tópico'}),
        label="Digite um assunto"
    )

