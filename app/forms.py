
from flask.ext.wtf import Form
from wtforms import BooleanField, RadioField
from wtforms.validators import Required


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

    medication = RadioField('Has your medication changed in the last two weeks?',
                 choices=[('0', 'No'), ('1', 'Yes')], validators=[Required()])
    medication_reason = BooleanField('Was it related to this condition?')
