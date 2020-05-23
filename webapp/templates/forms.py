from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class HostForm(FlaskForm):
    hostname = StringField('Hostname', [DataRequired(True)])
    timeperiod = SelectField('Time Period', choices=[('15m','15m'), ('1h','1h'), ('6h','6h'), ('1d','1d')], validate_choice=True)
    submitBtn = SubmitField("Get Information")