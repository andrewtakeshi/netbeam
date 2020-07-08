from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length


class HostForm(FlaskForm):
    hostname = StringField('Hostname', [DataRequired(True)])
    timeperiod = SelectField('Time Period', choices=[('15m','15m'), ('1h','1h'), ('6h','6h'), ('1d','1d')], validate_choice=True)
    submitBtn = SubmitField("Get Information")


class pscheduler_form(FlaskForm):
    pscheduler_source = StringField('Source', [DataRequired(True)])
    pscheduler_dest = StringField('Destination', [DataRequired(True)])
    numberRuns = IntegerField('Number of traceroutes')
    submitBtn = SubmitField('Get Information')