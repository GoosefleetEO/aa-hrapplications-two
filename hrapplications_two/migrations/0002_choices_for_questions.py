# Generated by Django 1.11.4 on 2017-08-23 19:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hrapplications_two', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_text', models.CharField(max_length=200, verbose_name='Choice')),
            ],
        ),
        migrations.AlterField(
            model_name='applicationquestion',
            name='title',
            field=models.CharField(max_length=254, verbose_name='Question'),
        ),
        migrations.AddField(
            model_name='applicationchoice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='hrapplications_two.ApplicationQuestion'),
        ),
    ]
