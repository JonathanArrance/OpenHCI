# -*- coding: utf-8 -*-
from django.db import models
import django_tables2 as tables


class Node(models.Model):
    COMPUTE_HALF = 'ch'
    COMPUTE_ONE = 'c1'
    STORAGE_HALF = 'sh'
    STORAGE_ONE = 's1'
    NODE_TYPE_CHOICES = (
        (COMPUTE_HALF, 'Compute 1/2'),
        (COMPUTE_ONE, 'Compute 1'),
        (STORAGE_HALF, 'Storage 1/2'),
        (STORAGE_ONE, 'Storage 1'),
    )

    name = models.CharField(max_length=100, unique=True)
    node_ip = models.CharField(max_length=15, unique=True)
    management_ip = models.CharField(max_length=15, unique=True)
    node_type = models.CharField(max_length=2, choices=NODE_TYPE_CHOICES,)


    def is_compute(self):
        return self.node_type in (self.COMPUTE_HALF, self.COMPUTE_ONE)

    def is_storage(self):
        return self.node_type in (self.STORAGE_HALF, self.STORAGE_ONE)

    def __unicode__(self):
        return self.name

class NodesTable(tables.Table):
    from django_tables2.utils import A  # alias for Accessor
    Id = tables.TemplateColumn('<a href="/nodes/{{record.name|urlencode}}/view">{{ record.name }}</a>', verbose_name="Node")

    class Meta:
        model = Node
        attrs = {"class": "paleblue"}


class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

class ProjectsTable(tables.Table):
    from django_tables2.utils import A  # alias for Accessor
    Id = tables.TemplateColumn('<a href="/projects/{{record.name|urlencode}}/view">{{ record.name }}</a>', verbose_name="Project")

    class Meta:
        model = Project
        attrs = {"class": "paleblue"}

class ImportLocal(models.Model):
    import_local = models.FileField(upload_to='/tmp/import.img')

