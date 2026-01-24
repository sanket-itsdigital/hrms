from django import forms
from chat.models import Message, ChatRoom
from accounts.models import User


class MessageForm(forms.ModelForm):
    """Form for sending messages"""
    
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Type your message...',
                'id': 'message-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True
        self.fields['content'].label = ''


class PersonalChatForm(forms.Form):
    """Form for creating/selecting a personal chat"""
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        }),
        label='Select User',
        help_text='Choose a user to start a personal chat'
    )
    
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if current_user:
            # Exclude current user and filter by organization
            queryset = User.objects.filter(
                is_active=True
            ).exclude(id=current_user.id)
            
            if current_user.organization:
                queryset = queryset.filter(organization=current_user.organization)
            
            self.fields['user'].queryset = queryset.order_by('first_name', 'last_name', 'username')
