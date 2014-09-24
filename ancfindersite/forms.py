from django import forms


class ANCUpdateForm(forms.Form):
    anc = forms.CharField(label='ANC', max_length=10)
    name = forms.CharField(label='Name', max_length=2083, required=False)
    email = forms.EmailField(label='Name', max_length=2083, required=False)
    mailing_address = forms.CharField(label='Mailing Address',
                                      widget=forms.Textarea, required=False)
    website = forms.URLField(label='Website', max_length=2083)
    website_screenshot = forms.URLField(label='Website Screenshot',
                                        max_length=2083, required=False)
    meeting_location = forms.CharField(label='Meeting Location',
                                       widget=forms.Textarea, required=False)
    meeting_date = forms.CharField(label='Meeting Date', max_length=2083,
                                   required=False)

    def send_email(self):
        pass


class SMDUpdateForm(forms.Form):
    smd = forms.CharField(label='SMD', max_length=10)
    official_name = forms.CharField(label='Official Name', max_length=2083,
                                    required=False)
    first_name = forms.CharField(label='First Name', max_length=2083,
                                 required=False)
    middle_name = forms.CharField(label='Middle Name', max_length=2083,
                                  required=False)
    nickname = forms.CharField(label='Nickname', max_length=2083,
                               required=False)
    last_name = forms.CharField(label='Last Name', max_length=2083,
                                required=False)
    suffix = forms.CharField(label='Suffix', max_length=2083, required=False)
    address = forms.CharField(label='Address', widget=forms.Textarea,
                              required=False)
    phone = forms.CharField(label='ANC', max_length=2083, required=False)
    email = forms.EmailField(label='Name', max_length=2083, required=False)
    position = forms.CharField(label='ANC', max_length=2083, required=False)
    website = forms.URLField(label='Website', max_length=2083, required=False)
    facebook = forms.URLField(label='Facebook', max_length=2083,
                              required=False)
    twitter = forms.URLField(label='Twitter', max_length=2083, required=False)
    linkedin = forms.URLField(label='Linkedin', max_length=2083,
                              required=False)
    other_url = forms.URLField(label='Other URL', max_length=2083,
                               required=False)
    listserv = forms.URLField(label='Listserv URL', max_length=2083,
                              required=False)
    committees = forms.CharField(label='Committee(s)', max_length=2083,
                                 required=False)
    key_initiatives = forms.CharField(label='Key Initiatives', max_length=2083,
                                      required=False)
    short_bio = forms.CharField(label='Short Bio', max_length=2083,
                                required=False)

    def send_email(self):
        pass
