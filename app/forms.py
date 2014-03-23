from flask.ext.wtf import Form
from wtforms import BooleanField, RadioField, TextField
from wtforms.validators import Length, Required


class BasicMoodForm(Form):
    moods = RadioField('What would you rate your mood out of 10?',
                       choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
                                ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'),
                                ('9', '9'), ('10', '10')],
                       validators=[Required()])


class AdvancedMoodForm(Form):
    moods = RadioField('What would you rate your mood out of 10?',
                       choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
                                ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'),
                                ('9', '9'), ('10', '10')],
                       validators=[Required()])

    hospital = RadioField('Have you been in hospital over the last two weeks?',
                 choices=[('0', 'No'), ('1', 'Yes')], validators=[Required()])
    hospital_reason = BooleanField('Was it related to this condition?')

    medication = RadioField('Has your medication changed in the last two \
                            weeks?',
                 choices=[('0', 'No'), ('1', 'Yes')], validators=[Required()])
    medication_reason = BooleanField('Was it related to this condition?')


class ConsentToStudyForm(Form):
    project_consent = BooleanField('I consent to this research project as \
                                   part of an understanding that the times I \
                                   use facebook will be analysed by MAPRC and \
                                   RMIT researchers and that this project \
                                   will ask me to rate my mood.',
                                   validators=[Required()])
    age_consent = BooleanField('I agree that I am between the ages of 18-30, \
                               am informed about this study\'s intent and \
                               general nature - including any possible risks \
                               of involvement - and that I am consenting for \
                               myself only and on no-ones behalf.',
                               validators=[Required()])
    diagnosed_consent = BooleanField('I acknowledge that I have a prior \
                                     diagnosis of bipolar disorder by an \
                                     Australian Doctor.',
                                     validators=[Required()])


class Episode(Form):
    date_of_episode = TextField('Date of episode', validators=[Required()])
    nature_of_episode = RadioField('Nature of episode', choices=[('0', 'Mania'),
                                   ('1', 'Depression')],
                                   validators=[Required()])
    hospitalisation = RadioField('Did this result in hospitalisation?',
                                 choices=[('0', 'No'), ('1', 'Yes')],
                                 validators=[Required()])
    medication_change = RadioField('Did this result in change to your \
                                   medication?',
                                   choices=[('0', 'No'), ('1', 'Yes')],
                                   validators=[Required()])
    suicidal_ideation = RadioField('Did you experience suicidal ideation?',
                                   choices=[('0', 'No'), ('1', 'Yes')],
                                   validators=[Required()])
