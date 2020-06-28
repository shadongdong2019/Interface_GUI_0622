# Generated by Django 3.0.7 on 2020-06-19 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InterfaceDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('p_id', models.IntegerField(verbose_name='项目ID')),
                ('p_name', models.CharField(max_length=100, verbose_name='项目名称')),
                ('i_id', models.IntegerField(verbose_name='接口ID')),
                ('i_name', models.CharField(max_length=100, verbose_name='接口名称')),
                ('case_path', models.CharField(blank=True, max_length=500, null=True, verbose_name='测试用例路径')),
                ('config_path', models.CharField(blank=True, max_length=500, null=True, verbose_name='配置文件路径')),
                ('image_path', models.CharField(blank=True, max_length=500, null=True, verbose_name='图片路径')),
                ('needs_path', models.CharField(blank=True, max_length=500, null=True, verbose_name='需求文档路径')),
                ('report_path', models.CharField(blank=True, max_length=500, null=True, verbose_name='需求文档路径')),
                ('download_path', models.CharField(blank=True, max_length=500, null=True, verbose_name='下载文件路径')),
                ('adder', models.CharField(blank=True, max_length=256, null=True)),
                ('addtime', models.DateTimeField(auto_now_add=True)),
                ('adderip', models.GenericIPAddressField(default='0.0.0.0')),
                ('status', models.IntegerField(choices=[(-1, '物理删除'), (0, '逻辑删除'), (100, '停用'), (200, '正常')], default=200)),
            ],
            options={
                'db_table': 'interface_details',
            },
        ),
        migrations.CreateModel(
            name='InterfaceManage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('p_id', models.IntegerField(verbose_name='项目ID')),
                ('p_name', models.CharField(max_length=100, verbose_name='项目名称')),
                ('i_name', models.CharField(max_length=100, verbose_name='接口名称')),
                ('p_path', models.CharField(max_length=500, verbose_name='接口路径')),
                ('adder', models.CharField(blank=True, max_length=256, null=True)),
                ('addtime', models.DateTimeField(auto_now_add=True)),
                ('adderip', models.GenericIPAddressField(default='0.0.0.0')),
                ('status', models.IntegerField(choices=[(0, '删除'), (100, '停用'), (200, '正常')], default=200)),
            ],
            options={
                'db_table': 'interface_manage',
            },
        ),
        migrations.CreateModel(
            name='ProjectsManage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('p_name', models.CharField(max_length=100, verbose_name='项目名称')),
                ('p_path', models.CharField(max_length=500, verbose_name='项目路径')),
                ('adder', models.CharField(blank=True, max_length=256, null=True)),
                ('addtime', models.DateTimeField(auto_now_add=True)),
                ('adderip', models.GenericIPAddressField(default='0.0.0.0')),
                ('status', models.IntegerField(choices=[(0, '删除'), (100, '停用'), (200, '正常')], default=200)),
            ],
            options={
                'db_table': 'projects_manage',
            },
        ),
    ]