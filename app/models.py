# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Accidente(models.Model):
    id_accidente = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.
    id_contrato = models.ForeignKey('Contrato', models.DO_NOTHING, db_column='id_contrato')
    fecha_accidente = models.TextField()  # This field type is a guess.
    estado_accidente = models.TextField()  # This field type is a guess.
    id_tipo_accidente = models.ForeignKey('TipoAccidente', models.DO_NOTHING, db_column='id_tipo_accidente')
    rut_profesional = models.ForeignKey('Profesional', models.DO_NOTHING, db_column='rut_profesional')

    class Meta:
        managed = False
        db_table = 'accidente'


class Administrador(models.Model):
    rut_administrador = models.TextField(primary_key=True)  # This field type is a guess.
    primer_nombre = models.TextField()  # This field type is a guess.
    segundo_nombre = models.TextField()  # This field type is a guess.
    apellido_p = models.TextField()  # This field type is a guess.
    apellido_m = models.TextField()  # This field type is a guess.
    telefono_administrador = models.TextField()  # This field type is a guess.
    direccion = models.TextField()  # This field type is a guess.
    id_usuario = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='id_usuario')

    class Meta:
        managed = False
        db_table = 'administrador'


class Afp(models.Model):
    id_afp = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'afp'


class Checklist(models.Model):
    id_checklist = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.
    fecha_registro = models.TextField()  # This field type is a guess.
    observaciones = models.TextField()  # This field type is a guess.
    extras = models.TextField()  # This field type is a guess.
    id_contrato = models.ForeignKey('Contrato', models.DO_NOTHING, db_column='id_contrato')
    rut_profesional = models.ForeignKey('Profesional', models.DO_NOTHING, db_column='rut_profesional')
    id_contador = models.ForeignKey('Contador', models.DO_NOTHING, db_column='id_contador')

    class Meta:
        managed = False
        db_table = 'checklist'


class Cliente(models.Model):
    rut_cliente = models.TextField(primary_key=True)  # This field type is a guess.
    razon_social = models.TextField()  # This field type is a guess.
    telefono = models.TextField()  # This field type is a guess.
    moroso = models.CharField(max_length=1)
    direccion = models.TextField()  # This field type is a guess.
    id_comuna = models.ForeignKey('Comuna', models.DO_NOTHING, db_column='id_comuna')
    id_usuario = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='id_usuario')
    id_rubro = models.ForeignKey('RubroCliente', models.DO_NOTHING, db_column='id_rubro')
    acta_constitucion = models.FileField(blank=True, null=True)  # This field type is a guess.
    fojas = models.FileField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'cliente'


class Comuna(models.Model):
    id_comuna = models.AutoField(primary_key=True)
    nombre_comuna = models.TextField()  # This field type is a guess.
    id_region = models.ForeignKey('Region', models.DO_NOTHING, db_column='id_region')

    class Meta:
        managed = False
        db_table = 'comuna'


class Contador(models.Model):
    cantidad = models.BigIntegerField()
    id_servicio = models.ForeignKey('Servicio', models.DO_NOTHING, db_column='id_servicio')
    id_contrato = models.ForeignKey('Contrato', models.DO_NOTHING, db_column='id_contrato')
    rut_profesional = models.ForeignKey('Profesional', models.DO_NOTHING, db_column='rut_profesional', blank=True, null=True)
    id_contador = models.BigIntegerField(primary_key=True)
    estado_servicio = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'contador'


class Contrato(models.Model):
    id_contrato = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.
    fecha_contrato = models.TextField()  # This field type is a guess.
    dia_pago = models.TextField()  # This field type is a guess.
    id_plan = models.ForeignKey('Plan', models.DO_NOTHING, db_column='id_plan')
    rut_cliente = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='rut_cliente')
    contrato_activo = models.TextField()  # This field type is a guess.
    monto_final = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'contrato'


class ContratoProfesional(models.Model):
    id_contrato_profesional = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.
    fecha_inicio = models.TextField()  # This field type is a guess.
    hora_extra = models.TextField()  # This field type is a guess.
    sueldo_liquido = models.BigIntegerField()
    sueldo_bruto = models.BigIntegerField()
    id_prevision = models.ForeignKey('Prevision', models.DO_NOTHING, db_column='id_prevision')
    id_tipo_contrato = models.ForeignKey('TipoContrato', models.DO_NOTHING, db_column='id_tipo_contrato')
    id_afp = models.ForeignKey(Afp, models.DO_NOTHING, db_column='id_afp')
    rut_profesional = models.OneToOneField('Profesional', models.DO_NOTHING, db_column='rut_profesional')
    contrato_activo = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'contrato_profesional'


class Material(models.Model):
    id_material = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'material'


class MaterialServicio(models.Model):
    cantidad = models.BigIntegerField()
    servicio_id_servicio = models.OneToOneField('Servicio', models.DO_NOTHING, db_column='servicio_id_servicio', primary_key=True)  # The composite primary key (servicio_id_servicio, material_id_material) found, that is not supported. The first column is selected.
    material_id_material = models.ForeignKey(Material, models.DO_NOTHING, db_column='material_id_material')

    class Meta:
        managed = False
        db_table = 'material_servicio'
        unique_together = (('servicio_id_servicio', 'material_id_material'),)


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    fecha_registro = models.TextField()  # This field type is a guess.
    monto = models.BigIntegerField()
    id_contrato = models.ForeignKey(Contrato, models.DO_NOTHING, db_column='id_contrato')
    id_tipo_pago = models.ForeignKey('TipoPago', models.DO_NOTHING, db_column='id_tipo_pago')

    class Meta:
        managed = False
        db_table = 'pago'


class Plan(models.Model):
    id_plan = models.AutoField(primary_key=True)
    fecha_creacion = models.TextField()  # This field type is a guess.
    tipo_plan = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'plan'


class Prevision(models.Model):
    id_prevision = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.
    tipo_prevision = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'prevision'


class Profesional(models.Model):
    rut_profesional = models.TextField(primary_key=True)  # This field type is a guess.
    primer_nombre = models.TextField()  # This field type is a guess.
    segundo_nombre = models.TextField()  # This field type is a guess.
    apellido_p = models.TextField()  # This field type is a guess.
    apellido_m = models.TextField()  # This field type is a guess.
    telefono_profesional = models.TextField()  # This field type is a guess.
    direccion = models.TextField()  # This field type is a guess.
    id_usuario = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='id_usuario')

    class Meta:
        managed = False
        db_table = 'profesional'


class Region(models.Model):
    id_region = models.AutoField(primary_key=True)
    nombre_region = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'region'


class RubroCliente(models.Model):
    id_rubro = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'rubro_cliente'


class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.
    valor = models.BigIntegerField()
    id_tipo_servicio = models.ForeignKey('TipoServicio', models.DO_NOTHING, db_column='id_tipo_servicio')
    estado_servicio = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'servicio'


class ServicioExtra(models.Model):
    id_servicio = models.ForeignKey(Servicio, models.DO_NOTHING, db_column='id_servicio')
    id_contrato = models.ForeignKey(Contrato, models.DO_NOTHING, db_column='id_contrato')
    fecha_extra = models.TextField()  # This field type is a guess.
    rut_profesional = models.ForeignKey(Profesional, models.DO_NOTHING, db_column='rut_profesional')

    class Meta:
        managed = False
        db_table = 'servicio_extra'


class ServicioPlan(models.Model):
    cantidad = models.BigIntegerField()
    id_servicio = models.OneToOneField(Servicio, models.DO_NOTHING, db_column='id_servicio', primary_key=True)  # The composite primary key (id_servicio, id_plan) found, that is not supported. The first column is selected.
    id_plan = models.ForeignKey(Plan, models.DO_NOTHING, db_column='id_plan')

    class Meta:
        managed = False
        db_table = 'servicio_plan'
        unique_together = (('id_servicio', 'id_plan'),)


class TipoAccidente(models.Model):
    id_tipo_accidente = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'tipo_accidente'


class TipoContrato(models.Model):
    id_tipo_contrato = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'tipo_contrato'


class TipoPago(models.Model):
    id_tipo_pago = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'tipo_pago'


class TipoServicio(models.Model):
    id_tipo_servicio = models.AutoField(primary_key=True)
    descripcion = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'tipo_servicio'


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    correo = models.TextField()  # This field type is a guess.
    contrasena = models.TextField()  # This field type is a guess.
    habilitado = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'usuario'


class Validacion(models.Model):
    id_validacion = models.AutoField(primary_key=True)
    nombre_validacion = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'validacion'


class ValidacionChecklist(models.Model):
    cumplido = models.CharField(max_length=1)
    id_validacion = models.OneToOneField(Validacion, models.DO_NOTHING, db_column='id_validacion', primary_key=True)  # The composite primary key (id_validacion, id_checklist) found, that is not supported. The first column is selected.
    id_checklist = models.ForeignKey(Checklist, models.DO_NOTHING, db_column='id_checklist')

    class Meta:
        managed = False
        db_table = 'validacion_checklist'
        unique_together = (('id_validacion', 'id_checklist'),)
