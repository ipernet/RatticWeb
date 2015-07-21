from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm, SelectMultiple, Select, PasswordInput

from models import Cred, Tag, Group
from widgets import CredAttachmentInput, CredIconChooser


class ExportForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'btn-password-visibility'}
    ))


class TagForm(ModelForm):
    class Meta:
        model = Tag


class CredForm(ModelForm):
    def __init__(self, requser, *args, **kwargs):
        # Check if a new attachment was uploaded
        if len(args) > 0 and args[1].get('attachment', None) is not None:
            self.changed_attachment = True
        else:
            self.changed_attachment = False

        super(CredForm, self).__init__(*args, **kwargs)

        # Limit the group options to groups that the user is in, except for staff (create-for-all)
        if not requser.is_staff:
            self.fields['group'].queryset = Group.objects.filter(user=requser)

        self.fields['group'].label = _('Owner Group')
        self.fields['groups'].label = _('Viewers Groups')

        # Make the URL invalid message a bit more clear
        self.fields['url'].error_messages['invalid'] = _("Please enter a valid HTTP/HTTPS URL")

    def save(self, *args, **kwargs):
        # Get the filename from the file object
        if self.changed_attachment:
            self.instance.attachment_name = self.cleaned_data['attachment'].name

        # Call save upstream to save the object
        super(CredForm, self).save(*args, **kwargs)

    class Meta:
        model = Cred
        # These field are not user configurable
        exclude = Cred.APP_SET
        widgets = {
            # Use chosen for the tag field
            'tags': SelectMultiple(attrs={'class': 'rattic-tag-selector'}),
            'group': Select(attrs={'class': 'rattic-group-selector'}),
            'groups': SelectMultiple(attrs={'class': 'rattic-group-selector'}),
            'password': PasswordInput(render_value=True, attrs={'class': 'btn-password-generator btn-password-visibility'}),
            'attachment': CredAttachmentInput,
            'iconname': CredIconChooser,
        }
