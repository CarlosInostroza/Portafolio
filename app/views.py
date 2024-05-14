from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from django.http import HttpResponseForbidden
from app.models import *
from django.http import JsonResponse
from .Soap import SOAPClient
import time
import os
from django.db.models import Sum, F
from rut_chile import rut_chile

# Create your views here.
def index(request):
    return render(request, 'app/index.html')
def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        # Realiza la llamada al servicio web para la autenticación
        soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')
        response = soap_client.call_method('login_Cliente_web', correo=correo, contrasena=contrasena)

        if response is not None:
            if response.rut_cliente is not None:

                usuario={
                        'contrasena_usuario':response.contrasena_usuario,
                        'correo_usuario':response.correo_usuario,
                        'direccion':response.direccion,
                        'id_comuna':response.id_comuna,
                        'id_rubro':response.id_rubro,
                        'moroso': response.moroso,
                        'razon_social': response.razon_social,
                        'rut_cliente': response.rut_cliente,
                        'telefono': response.telefono,
                        'usuario_id': response.usuario_id

                }
                request.session['usuario']=usuario
                return redirect('cliente')
            else:
                return render(request, 'app/login.html', {'error_message': 'Usuario Deshabilitado, espere que se habilite su cuenta.'})
        else:
            # Si no se recibió respuesta del servicio, muestra un mensaje de error predeterminado
            
            return render(request, 'app/login.html', {'error_message': 'Error al ingresar, compruebe su correo y contraseña.'})
    return render(request, 'app/login.html')
def cerrar_sesion(request):
    if 'usuario' in request.session:
        del request.session['usuario']
        return redirect('login')
    else:
        return redirect('login')
    
def register(request):

    comunas= Comuna.objects.all()
    rubro= RubroCliente.objects.all()
    datos={
        'listaComuna' : comunas,
        'listaRubro' : rubro
    }


    if request.method == 'POST':
        try:
            # Obtén los datos del formulario
            rut_cliente = request.POST.get('rut_empresa')
            rut_obj = rut_chile.is_valid_rut(rut_cliente)
            print(rut_obj)
            if rut_obj is False:
                messages.error(request, 'Error: Ingrese un RUT válido')
                return render(request, 'app/register.html', datos)
            
            razon_social = request.POST.get('razon_social')
            telefono = request.POST.get('telefono')
            moroso ='N'
            direccion = request.POST.get('direccion')
            comuna = request.POST.get('comuna')
            correo = request.POST.get('correo')
            contrasena = request.POST.get('contrasena')
            rubro = request.POST.get('rubro')
            confirmarcontrasena = request.POST.get('confirmarContrasena')
            
            acta_constitucion = request.FILES.get('acta_constitucion')
            fojas = request.FILES.get('fojas')

            pdf_directory = r'C:\Users\carlo\Desktop\PORTAFOLIO\app\static\app\pdf'

            acta_constitucion_path = os.path.join(pdf_directory, acta_constitucion.name)
            fojas_path = os.path.join(pdf_directory, fojas.name)
            os.makedirs(os.path.dirname(acta_constitucion_path), exist_ok=True)
            os.makedirs(os.path.dirname(fojas_path), exist_ok=True)
            with open(acta_constitucion_path, 'wb') as acta_file:
                for chunk in acta_constitucion.chunks():
                    acta_file.write(chunk)

            with open(fojas_path, 'wb') as fojas_file:
                for chunk in fojas.chunks():
                    fojas_file.write(chunk)

            if not rut_cliente.strip():
                messages.error(request, 'Error: Ingrese Rut')
            elif not razon_social or len(razon_social) < 2:
                messages.error(request, 'Error: Ingrese Razón social')
            elif not telefono or not telefono.isdigit():
                messages.error(request, 'Error: Ingrese teléfono valido(solo números)')
            elif not direccion:
                messages.error(request, 'Error: Ingrese dirección')
            elif not correo or len(correo) < 10:
                messages.error(request, 'Error: Ingrese correo')
            elif not contrasena or len(contrasena) < 6:
                messages.error(request, 'Error: Ingrese contraseña valida y de mas de 6 caracteres')
            elif not acta_constitucion:
                messages.error(request, 'Error: Adjunte Acta')
            elif not fojas:
                messages.error(request, 'Error: Adjunte Fojas')
            elif contrasena==confirmarcontrasena:
                soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')

                # Llama al método en el servicio web SOAP y proporciona los argumentos
                
                response = soap_client.call_method('agregar_cliente_usuario', rut_cliente=rut_cliente, razon_social=razon_social,telefono=telefono,moroso=moroso,
                                                                                    direccion=direccion, comuna=comuna,
                                                                                    correo=correo, contrasena=contrasena,rubro=rubro,acta_constitucion=acta_constitucion_path,fojas=fojas_path)
                if response is True :
                    messages.success(request, 'Registro exitoso. ¡Inicia sesión ahora!')
                    
                    return redirect(login)
                else:
                    # Procesa la respuesta del servicio web como desees
                    messages.error(request, 'Error: Ingrese todos los datos pedidos')
            else:
                messages.error(request, 'Error: Contraseñas no coinciden')
        except Exception as e:
            print(e)
            messages.error(request, 'Error: Ingrese todos los datos pedidos')
    return render(request, 'app/register.html', datos)
def cliente(request):
    if request.session.get('usuario'):
        usuario = request.session['usuario']
        if 'contrato' in request.session:
            del request.session['contrato']
        if 'servicios_cliente' in request.session:
            del request.session['servicios_cliente']

        contrato = request.session.get('contrato', None)
        rut_cliente = usuario['rut_cliente']


        soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')

        response = soap_client.call_method('listar_Contratos_Por_Cliente', rut_cliente=rut_cliente)
        

        for x in response:
            if x.contratoActivo == 'Si':
                
                contrato={
                                'contrato_activo':x.contratoActivo,
                                'descripcion_param':x.descripcion,
                                'dia_pago_param':x.diaPago,
                                'fecha_contrato_param':x.fechaContrato,
                                'id_contrato_param': x.idContrato,
                                'id_plan_param': x.idPlan,
                                'rut_cliente_param': x.rutCliente,
                                'contrato_activo' : 'Si',
                                'monto_final' : x.montoFinal
                            }
                request.session['contrato']=contrato
                response2 = soap_client.call_method('verificar_servicios_disponibles1', id_contrato=contrato['id_contrato_param'])     
                if response2:
                    servicios=[]
                    for y in response2:
                        servicio={'serviciosConRut': y.serviciosConRut,
                                  'serviciosDisponibles': y.serviciosDisponibles,
                                  'tipoServicio': y.tipoServicio,
                                  'totalServicios': y.totalServicios
                                }
                        servicios.append(servicio)
                        print(servicio)
                    return render(request, 'app/cliente.html', {'usuario': usuario, 'contrato': contrato,'servicio':servicios})
                else:
                    return render(request, 'app/cliente.html', {'usuario': usuario, 'contrato': contrato})


            elif x.contratoActivo == 'No':
                contrato={
                                'contrato_activo':x.contratoActivo,
                                'descripcion_param':x.descripcion,
                                'dia_pago_param':x.diaPago,
                                'fecha_contrato_param':x.fechaContrato,
                                'id_contrato_param': x.idContrato,
                                'id_plan_param': x.idPlan,
                                'rut_cliente_param': x.rutCliente,
                                'contrato_activo' : 'No',
                                'monto_final' : x.montoFinal

                            }
                request.session['contrato']=contrato
                return render(request, 'app/cliente.html', {'usuario': usuario, 'contrato': contrato})
        else:
            mensaje = "No tienes un contrato en este momento."
            return render(request, 'app/cliente.html', {'usuario': usuario, 'mensaje': mensaje})
    else:
        return redirect(login)

    
def firmaContrato(request):
    if request.session.get('usuario'):
        usuario= request.session['usuario']
        contrato= request.session.get('contrato',None)
        plan_personalizado = request.session.get('plan_personalizado', [])
        valor_final = request.session['valor_final']
        planes=[]
        if contrato is None:

            for plan in plan_personalizado:
                id_planActual = plan['id_plan']
                tipo_servicio = plan['Tipo_servicio_id']
                descripcion1 = plan['Descripcion']
                cantidad = plan['Cantidad']
                rut_plan = plan['rut']
                valor = plan['valor']
                
                # Agregar los datos de este plan a la lista de planes
                planes.append({
                    'id_plan': id_planActual,
                    'tipo_servicio_id': tipo_servicio,
                    'descripcion': descripcion1,
                    'cantidad': cantidad,
                    'rut': rut_plan,
                    'valor': valor
                })

            if request.method == 'POST':
                    try:
                        # Obtén los datos del formulario
                        
                        id_plan=request.session['id_plan_primero']
                        fecha_contrato = request.POST.get('fecha_contrato')
                        rut_cliente = usuario['rut_cliente']
                        razon_social = usuario['razon_social']
                        descripcion = f"Contrato para {razon_social}"
                        monto_final=int(float(valor_final))

                        # Crea una instancia del cliente SOAP y especifica la URL del servicio web
                        soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')

                        # Llama al método en el servicio web SOAP y proporciona los argumentos
                        response = soap_client.call_method('crear_contrato_cliente1',id_plan_param=id_plan ,fecha_contrato_param=fecha_contrato,descripcion_param=descripcion,rut_cliente_param=rut_cliente,monto_final_param=monto_final)
                        if response:
                                contrato={
                                'contrato_activo':response.contrato_activo,
                                'descripcion_param':response.descripcion_param,
                                'dia_pago_param':response.dia_pago_param,
                                'fecha_contrato_param':response.fecha_contrato_param,
                                'id_contrato_param': response.id_contrato_param,
                                'id_plan_param': response.id_plan_param,
                                'rut_cliente_param': response.rut_cliente_param,
                                'valor_final':response.monto_final_param

                            }
                                request.session['contrato']=contrato
                                del request.session['valor_final']
                                messages.success(request, 'Registro exitoso.')

                                soap_client.call_method('agregar_cantidad_contador',id_contrato=contrato['id_contrato_param'])

                                return redirect('pago')
                        else:
                            print(response)
                            messages.error(request, 'Error: Ingrese los datos correspondientes')
                    except Exception as e:
                        messages.error(request, {'Error': str(e)})
                
            return render(request, 'app/firmaContrato.html',{'usuario': usuario,'plan_personalizado':plan_personalizado,'valor_final':valor_final,'planes': planes,'contrato':contrato})
        else:
            return render(request, 'app/firmaContrato.html',{'usuario': usuario,'plan_personalizado':plan_personalizado,'valor_final':valor_final,'planes': planes})
    else:
        return redirect(login)


def resetear_datos(request):

    if 'valor_final' in request.session:
        del request.session['valor_final']  # Elimina el valor_final de la sesión
    if 'id_plan_primero' in request.session:
        del request.session['id_plan_primero'] 
    if 'id_plan_primero2' in request.session:
        del request.session['id_plan_primero2']
    if 'id_plan_primero3' in request.session:
        del request.session['id_plan_primero3']
    if 'id_plan_primero4' in request.session:
        del request.session['id_plan_primero4']
    if plan_personalizado:
        plan_personalizado.clear()
        return redirect('planPersonalizado')
    if plan_personalizado2:
        plan_personalizado2.clear()
        return redirect('extraCapacitacion')
    elif plan_personalizado3:
        plan_personalizado3.clear()
        return redirect('extraVisita')
    elif plan_personalizado4:
        plan_personalizado4.clear()
        return redirect('extraAsesoria')  # Limpia la lista plan_personalizado
    else:
        messages.error(request, 'No hay datos por borrar')
        return redirect(request.META.get('HTTP_REFERER'))




def pago(request):
    if request.session.get('usuario'):
        print('Autenticado')
        usuario = request.session['usuario']
        contrato = request.session['contrato']
        monto=contrato['valor_final']

        if request.method == 'POST':
            try:
                id_contrato = contrato['id_contrato_param']
                id_tipo_pago = request.POST.get('tipoPago')
                monto_final=int(float(monto))
                
                soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')
                response = soap_client.call_method('crear_pago',id_contrato=id_contrato ,id_tipo_pago=id_tipo_pago, monto=monto_final)

                if response:
                    
                    messages.success(request, 'Pago exitoso.')
                    if 'valor_final' in request.session:
                        del request.session['valor_final']  
                    if 'id_plan_primero' in request.session:
                        del request.session['id_plan_primero'] 
                    if 'id_plan_primero2' in request.session:
                        del request.session['id_plan_primero2']
                    if 'id_plan_primero3' in request.session:
                        del request.session['id_plan_primero3']
                    if 'id_plan_primero4' in request.session:
                        del request.session['id_plan_primero4']
                    if plan_personalizado:
                        plan_personalizado.clear()
                        del request.session['plan_personalizado']
                    elif plan_personalizado2:
                        plan_personalizado2.clear()
                        del request.session['plan_personalizado2']
                    elif plan_personalizado3:
                        plan_personalizado3.clear()
                        del request.session['plan_personalizado3']
                    elif plan_personalizado4:
                        plan_personalizado4.clear()
                        del request.session['plan_personalizado4']
                    elif plan_personalizado5:
                        plan_personalizado5.clear()
                        del request.session['plan_personalizado5']

                    return redirect(pagoRealizado)
                else:

                    messages.error(request, 'Error: No se proceso el pago')
            except Exception as e:
                        messages.error(request, {'Error': str(e)})

        return render(request, 'app/pago.html',{'usuario':usuario,'contrato':contrato,'plan_personalizado':plan_personalizado})
    else:
        return redirect(login)

    

def pago2(request):
    if request.session.get('usuario'):
        print('Autenticado')
        usuario = request.session['usuario']
        contrato = request.session['contrato']
        monto=contrato['monto_final']

        preference = None
        if request.method == 'POST':
            try:
                id_contrato = contrato['id_contrato_param']
                id_tipo_pago = request.POST.get('tipoPago')
                monto_final=monto

                soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')
                response = soap_client.call_method('crear_pago',id_contrato=id_contrato ,id_tipo_pago=id_tipo_pago, monto=monto_final)

                if response:
                    
                    messages.success(request, 'Pago exitoso.')

                    
                    if 'id_plan_primero2' in request.session:
                        del request.session['id_plan_primero2']

                    
                    if 'id_plan_primero3' in request.session:
                        del request.session['id_plan_primero3']

                    
                    if 'id_plan_primero4' in request.session:
                        del request.session['id_plan_primero4']
                    
                    if plan_personalizado2:
                        del request.session['plan_personalizado2']
                        plan_personalizado2.clear()
                    if plan_personalizado3:
                        del request.session['plan_personalizado3']
                        plan_personalizado3.clear()
                    if plan_personalizado4:
                        del request.session['plan_personalizado4']
                        plan_personalizado4.clear()
                    if plan_personalizado5:
                        del request.session['plan_personalizado5']
                        plan_personalizado5.clear()
                    
                    soap_client.call_method('borrar_extras',p_id_contrato=id_contrato)

                    return redirect(login)
                else:

                    messages.error(request, 'Error: No se proceso el pago')
            except Exception as e:
                        messages.error(request, {'Error': str(e)})

        return render(request, 'app/pago2.html',{'usuario':usuario,'contrato':contrato,'plan_personalizado':plan_personalizado,'monto':monto})
    else:
        return redirect(login)


def pagoRealizado(request):
    if request.session.get('usuario'):
        print('Autenticado')
    else:
        return redirect(login)
    return render(request, 'app/pagoRealizado.html')

plan_personalizado=[]

def planPersonalizado(request):

    if request.session.get('usuario'):
        usuario= request.session['usuario']
        print('Autenticado')
        tipo_servicio= TipoServicio.objects.all()
        id_plan_primero= request.session.get('id_plan_primero',None)
        valor_final= request.session.get('valor_final',0)

        if id_plan_primero is None:

            if request.method == 'POST':
                try:
                    # Obtén los datos del formulario
                    

                    servicio = request.POST.get('servicio')
                    
                    descripcion=""
                    
                    if servicio == "1":
                        descripcion = "Asesoria"
                    elif servicio == "2":
                        descripcion = "Visita"
                    elif servicio == "3":
                        descripcion = "Capacitación"
                    cantidad = request.POST.get('cantidad')
                    

                    # Crea una instancia del cliente SOAP y especifica la URL del servicio web
                    soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')

                    # Llama al método en el servicio web SOAP y proporciona los argumentos
                    response = soap_client.call_method('crear_plan_personalizado1',tipoServicioId=servicio, descripcion=descripcion,cantidad=cantidad)
                    if response:
                        
                        request.session['id_plan_primero'] = response.idPlan
                        plan_personalizado.append({
                            'id_plan': response.idPlan,
                            'Tipo_servicio_id': servicio,
                            'Descripcion': descripcion,
                            'Cantidad': cantidad,
                            'rut': usuario['rut_cliente'],
                            'valor':response.valorTotal
                            
                        })
                        valor_final+= response.valorTotal
                        request.session['valor_final']=valor_final
                        request.session['plan_personalizado'] = plan_personalizado
                        messages.success(request, 'Registro exitoso.')
                        return redirect(planPersonalizado)
                    else:
                        messages.error(request, 'Error: Ingrese los datos correspondientes')
                except Exception as e:
                    messages.error(request, {'Error': str(e)})

        planes_del_usuario = [plan for plan in plan_personalizado if plan['id_plan'] == id_plan_primero]
        datos={
        'listaServicio' : tipo_servicio,
        'plan_personalizado' : planes_del_usuario,
        'usuario' : usuario,
        'valor_final' : valor_final
        }
        if request.method == 'POST':
            try:
                # Obtén los datos del formulario
                
                id_plan= request.session['id_plan_primero']
                servicio = request.POST.get('servicio')
                descripcion=""
                    
                if servicio == "1":
                    descripcion = "Asesoria"
                elif servicio == "2":
                    descripcion = "Visita"
                elif servicio == "3":
                    descripcion = "Capacitación"

                cantidad = request.POST.get('cantidad')
                

                # Crea una instancia del cliente SOAP y especifica la URL del servicio web
                soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')

                # Llama al método en el servicio web SOAP y proporciona los argumentos
                response = soap_client.call_method('agregar_servicios_plan1',Tipo_servicio_id=servicio,Descripcion=descripcion,Cantidad=cantidad,id_plan=id_plan)
                if response:
                    
                    plan_personalizado.append({
                        'id_plan': id_plan,
                        'Tipo_servicio_id': servicio,
                        'Descripcion': descripcion,
                        'Cantidad': cantidad,
                        'rut': usuario['rut_cliente'],
                        'valor':response.valor_total
                    })

                    valor_final+= response.valor_total
                    request.session['valor_final']=valor_final
                    request.session['plan_personalizado'] = plan_personalizado
                    datos['valor_final']=valor_final
                    messages.success(request, 'Registro exitoso.')
                    return redirect(planPersonalizado)
                else:
                    messages.error(request, 'Error: Ingrese los datos correspondientes')
            except Exception as e:
                messages.error(request, {'Error': str(e)})

        return render(request, 'app/planPersonalizado.html',datos)
    else:
        return redirect(login)

def solicitarServicio(request):
    if request.session.get('usuario'):
        print('Autenticado')
    else:
        return redirect(login)
    return render(request, 'app/solicitarServicio.html')
def perfil(request):
    if request.session.get('usuario'):
        print('Autenticado')
        usuario = request.session['usuario']
        return render(request, 'app/perfil.html',{'usuario':usuario})
    else:
        return redirect(login)


def contrato(request):
    if request.session.get('usuario'):
        print('Autenticado')
        usuario = request.session['usuario']
        contrato = request.session['contrato']
        plan = ServicioPlan.objects.filter(id_plan=contrato['id_plan_param']).select_related('id_servicio','id_plan')
        resumen_planes = {}
        for servicio_plan in plan:
            id_plan = servicio_plan.id_plan.id_plan
            valor = servicio_plan.id_servicio.valor
            cantidad = servicio_plan.cantidad
            precio_final = valor * cantidad

            if id_plan in resumen_planes:
                resumen_planes[id_plan]['suma_valores'] += precio_final
                resumen_planes[id_plan]['servicios'].append(servicio_plan.id_servicio.descripcion)
            else:
                resumen_planes[id_plan] = {
                    'suma_valores': precio_final,
                    'servicios': [servicio_plan.id_servicio.descripcion],
                    'cantidad' : cantidad
                }
        if request.method == 'POST':
            try:
                soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')
                response = soap_client.call_method('desactivar_contrato',id_contrato=contrato['id_contrato_param'])
                if response is True:
                    redirect(cliente)
                    messages.success(request,'Se desactivo su contrato.')
                else:
                    messages.error(request, 'Error: No se pudo borrar su contrato')
            except Exception as e:    
                print(e)
        return render(request, 'app/contrato.html',{'contrato':contrato, 'usuario':usuario,'resumen_planes':resumen_planes})
    else:
        return redirect(login)


def test(request):
    if request.method == 'POST':
        try:
            # Obtén los datos del formulario
            rut_administrador = request.POST.get('rut')
            primer_nombre = request.POST.get('primer_nombre')
            segundo_nombre = request.POST.get('segundo_nombre')
            apellido_p = request.POST.get('apellido_paterno')
            apellido_m = request.POST.get('apellido_materno')
            telefono_administrador = request.POST.get('telefono')
            direccion_administrador = request.POST.get('direccion')
            correo = request.POST.get('correo')
            contrasena = request.POST.get('contraseña')

            # Crea una instancia del cliente SOAP y especifica la URL del servicio web
            soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')

            # Llama al método en el servicio web SOAP y proporciona los argumentos
            response = soap_client.call_method('agregar_administador_usuario', rut_administrador=rut_administrador, primer_nombre=primer_nombre,segundo_nombre=segundo_nombre,
                                                                                apellido_p=apellido_p, apellido_m=apellido_m,
                                                                                telefono_administrador=telefono_administrador, direccion_administrador=direccion_administrador, correo=correo, contrasena=contrasena)
            if response:
                return JsonResponse({'response': 'si'})
            else:
                return JsonResponse({'response': 'no'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        
    return render(request, 'app/test.html')
def accidente(request):
    if request.session.get('usuario'):
        print('Autenticado')
        usuario = request.session['usuario']
        contrato = request.session['contrato']
        soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')
        response = soap_client.call_method('listar_accidentes1')

        ac_contrato = []
        
        if response:
            for accidente in response:
                id_contrato_accidente=accidente['id_contrato']
                if contrato['id_contrato_param'] == id_contrato_accidente:

                    descripcion = accidente['descripcion']
                    estado_accidente = accidente['estado_accidente']
                    fecha_accidente = accidente['fecha_accidente']
                    id_accidente = accidente['id_accidente']

                    if accidente['id_tipo_accidente'] == 1:
                        id_tipo_accidente="Caida"
                    elif accidente['id_tipo_accidente'] == 2:
                        id_tipo_accidente="Aplastamiento"
                    elif accidente['id_tipo_accidente'] == 3:
                        id_tipo_accidente="Sobreesfuerzo"
                    elif accidente['id_tipo_accidente'] == 4:
                        id_tipo_accidente="Otros"


                    ac_contrato.append({
                        'descripcion':descripcion,
                        'estado_accidente':estado_accidente,
                        'fecha_accidente':fecha_accidente,
                        'id_accidente':id_accidente,
                        'id_tipo_accidente':id_tipo_accidente
                    })



        return render(request, 'app/accidente.html',{'accidentes':ac_contrato})
    else:
        return redirect(login)

def envioAccidente(request):
    if request.session.get('usuario'):
        print('Autenticado')
        contrato = request.session['contrato']

        if request.method == 'POST':
            try:
                # Obtén los datos del formulario
                descripcion = request.POST.get('descripcion')
                id_contrato = contrato['id_contrato_param']
                fecha_accidente = request.POST.get('fecha_accidente')
                id_tipo_accidente = request.POST.get('id_tipo_accidente')

                if not descripcion.strip():
                    messages.error(request, 'Error: Ingrese la descripción')
                elif not fecha_accidente:
                    messages.error(request, 'Error: Ingrese la fecha del accidente')
                elif not id_tipo_accidente:
                    messages.error(request, 'Error: Seleccione el tipo de accidente')
                else:
                    soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')
                    response = soap_client.call_method('crear_accidentes',descripcion=descripcion,id_contrato=id_contrato,fecha_accidente=fecha_accidente,id_tipo_accidente=id_tipo_accidente)
                    
                    if response is True:
                        messages.success(request, 'Envio de accidente completo')
                    else:
                        messages.error(request, 'Error: Ingrese los datos correspondientes')
            except Exception as e:
                    messages.error(request, {'Error: Ingrese todos los datos pedidos'})
        return render(request, 'app/envioAccidente.html')
    else:
        return redirect(login)

def verCapacitacion(request):
    if request.session.get('usuario'):
        print('Autenticado')
        return render(request, 'app/verCapacitacion.html')
    else:
        return redirect(login)
    
def vistaAccidente(request):
    if request.session.get('usuario'):
        print('Autenticado')
    else:
        return redirect(login)
    return render(request, 'app/vistaAccidente.html')
def capacitaciones(request):
    if request.session.get('usuario'):
        print('Autenticado')


        return render(request, 'app/capacitaciones.html')
    else:
        return redirect(login)
def servicios(request):
    if request.session.get('usuario'):
        print('Autenticado')
        usuario = request.session['usuario']
        contrato = request.session['contrato']
        soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')
        response = soap_client.call_method('listar_Contador_por_contrato1',id_contrato=contrato['id_contrato_param'])

        servicios = []
        
        if response:
            for x in response:
                
                rut_profesional = x['rut_profesional']
                estado_servicio = x['estado_servicio']
                id_servicio = x['id_servicio']
                fecha_registro = x['fecha_registro']
                tipo_servicio = x['tipo_servicio']
                id_contador=x['id_contador']
                
                if fecha_registro is None:
                    fecha_registro = ""
                if rut_profesional is None:
                    rut_profesional = ""

                servicios.append({
                    'rut_profesional':rut_profesional,
                    'estado_servicio':estado_servicio,
                    'id_servicio':id_servicio,
                    'fecha_registro':fecha_registro,
                    'tipo_servicio':tipo_servicio,
                    'id_contador':id_contador
                })

            
            if request.method == 'POST':
                try:
                    for key, value in request.POST.items():
                        if key.startswith('id_contador_'):
                            id_contador1 = key[len('id_contador_'):]

                    response1=soap_client.call_method('cambiar_estado_contador',id_contador=id_contador1)
                    print(response1)
                    messages.success(request, 'Servicio solicitado correctamente.')
                    return redirect('servicios')
                except Exception as e:
                    messages.error(request, {'Error': str(e)})


        return render(request, 'app/servicios.html',{'servicios':servicios})

    else:
        return redirect(login)

plan_personalizado2=[]
def extraCapacitacion(request):
    if request.session.get('usuario'):
        print('Autenticado')
        usuario= request.session['usuario']
        contrato = request.session['contrato']
        tipo_servicio= TipoServicio.objects.get(id_tipo_servicio=3)
        id_plan_primero2= request.session.get('id_plan_primero2',None)
        valor_final= request.session.get('valor_final',0)
        
        if id_plan_primero2 is None:

            if request.method == 'POST':
                try:
                    # Obtén los datos del formulario
                    
                    id_contrato=contrato['id_contrato_param']
                    servicio = request.POST.get('servicio')
                    descripcion = "Capacitación extra"
                    

                    # Crea una instancia del cliente SOAP y especifica la URL del servicio web
                    soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')

                    # Llama al método en el servicio web SOAP y proporciona los argumentos
                    response = soap_client.call_method('insertar_extras',descripcion=descripcion,tipo_servicio_id=servicio,rut_profesional="",id_contrato=id_contrato)
                    if response is True:
                        messages.success(request, 'Registro exitoso. Por favor espere el proceso de su solicitud.')
                        return redirect(extraCapacitacion)
                    else:
                        messages.error(request, 'Error: Ingrese los datos correspondientes')
                except Exception as e:
                    messages.error(request, {'Error': str(e)})

        datos={
        'listaServicio' : tipo_servicio,
        'usuario' : usuario
        }
        return render(request, 'app/extraCapacitacion.html',datos)

    else:
        return redirect(login)

plan_personalizado3=[]
def extraVisita(request):
    if request.session.get('usuario'):
        print('Autenticado')
        usuario= request.session['usuario']
        contrato = request.session['contrato']
        tipo_servicio= TipoServicio.objects.get(id_tipo_servicio=2)
        id_plan_primero3= request.session.get('id_plan_primero3',None)
        valor_final= request.session.get('valor_final',0)
        
        if id_plan_primero3 is None:

            if request.method == 'POST':
                try:
                    # Obtén los datos del formulario
                    
                    id_contrato=contrato['id_contrato_param']
                    servicio = request.POST.get('servicio')
                    descripcion = "Visita extra"
                    

                    # Crea una instancia del cliente SOAP y especifica la URL del servicio web
                    soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')

                    # Llama al método en el servicio web SOAP y proporciona los argumentos
                    response = soap_client.call_method('insertar_extras',descripcion=descripcion,tipo_servicio_id=servicio,rut_profesional="",id_contrato=id_contrato)
                    if response is True:
                        messages.success(request, 'Registro exitoso. Por favor espere el proceso de su solicitud.')
                        return redirect(extraVisita)
                    else:
                        messages.error(request, 'Error: Ingrese los datos correspondientes')
                except Exception as e:
                    messages.error(request, {'Error': str(e)})

        planes_del_usuario = [plan for plan in plan_personalizado3 if plan['idExtra'] == id_plan_primero3]
        datos={
        'listaServicio' : tipo_servicio,
        'plan_personalizado3' : planes_del_usuario,
        'usuario' : usuario,
        'valor_final' : valor_final
        }
        return render(request, 'app/extraVisita.html',datos)

    else:
        return redirect(login)

plan_personalizado4=[]
def extraAsesoria(request):
    if request.session.get('usuario'):
        print('Autenticado')
        usuario= request.session['usuario']
        contrato = request.session['contrato']
        tipo_servicio= TipoServicio.objects.get(id_tipo_servicio=1)
        id_plan_primero4= request.session.get('id_plan_primero4',None)
        valor_final= request.session.get('valor_final',0)
        
        if id_plan_primero4 is None:

            if request.method == 'POST':
                try:
                    # Obtén los datos del formulario
                    
                    id_contrato=contrato['id_contrato_param']
                    servicio = request.POST.get('servicio')
                    descripcion = "Asesoria extra"
                    

                    # Crea una instancia del cliente SOAP y especifica la URL del servicio web
                    soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')

                    # Llama al método en el servicio web SOAP y proporciona los argumentos
                    response = soap_client.call_method('insertar_extras',descripcion=descripcion,tipo_servicio_id=servicio,rut_profesional="",id_contrato=id_contrato)
                    if response is True:
                        messages.success(request, 'Registro exitoso. Por favor espere el proceso de su solicitud.')
                        return redirect(extraAsesoria)
                    else:
                        messages.error(request, 'Error: Ingrese los datos correspondientes')
                except Exception as e:
                    messages.error(request, {'Error': str(e)})

        planes_del_usuario = [plan for plan in plan_personalizado4 if plan['idExtra'] == id_plan_primero4]
        datos={
        'listaServicio' : tipo_servicio,
        'plan_personalizado4' : planes_del_usuario,
        'usuario' : usuario,
        'valor_final' : valor_final
        }
        return render(request, 'app/extraAsesoria.html',datos)

    else:
        return redirect(login)

plan_personalizado5=[]
def plan(request):
    if request.session.get('usuario'):
        print('Autenticado')
        usuario= request.session['usuario']
        valor_final= request.session.get('valor_final',0)
        soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')
        response = soap_client.call_method('listar_planes_tipo2')

        
        if response:

            resumen_planes = {}
            for servicio_plan in response:
                id_plan = servicio_plan['idPlan']
                valor = servicio_plan['valorServicio']
                cantidad = servicio_plan['cantidad']
                valor_total = servicio_plan['valorTotal']
                tipo_servicio=servicio_plan['tipoServicioDesc']



                if id_plan in resumen_planes:
                    resumen_planes[id_plan]['valor'] += valor_total
                    resumen_planes[id_plan]['Descripcion'].append(tipo_servicio)
                else:
                    resumen_planes[id_plan] = {
                        'id_plan': id_plan,
                        'valor': valor_total,
                        'Descripcion': [tipo_servicio],
                        'Cantidad' : cantidad,
                        'Tipo_servicio_id': tipo_servicio

                    }
  
            if request.method == 'POST':
                try:
                    plan_id = request.POST.get('plan_id')
                    suma_valores = request.POST.get('suma_valores')
                    servicios = request.POST.get('servicios')
                    cantidad1 = request.POST.get('cantidad')
                    tipo_servicio1=request.POST.get('tipo_servicio')

                    plan_personalizado5.append({
                        'id_plan': plan_id,
                        'Tipo_servicio_id': "Plan Fijo",
                        'Descripcion': "Plan Fijo",
                        'Cantidad': "Plan Fijo",
                        'rut': usuario['rut_cliente'],
                        'valor':suma_valores                           
                    })
                    request.session['id_plan_primero'] = plan_id
                    request.session['valor_final']=suma_valores
                    request.session['plan_personalizado'] = plan_personalizado5
                    plan_personalizado5.clear()
                    return redirect(firmaContrato)

                except Exception as e:
                    messages.error(request, {'Error': str(e)})

        else:
            messages.error(request, 'No hay planes disponibles')
        datos = {
            'resumen_planes': resumen_planes
        }
        return render(request, 'app/plan.html', datos)
    else:
        return redirect(login)
    
    

def sobreNosotros(request):

    return render(request, 'app/sobreNosotros.html')


def terminosYcondiciones(request):

    return render(request, 'app/terminosYcondiciones.html')

def listarExtra(request):
    if request.session.get('usuario'):
        print('Autenticado')
        usuario = request.session['usuario']
        contrato = request.session['contrato']
        soap_client = SOAPClient('http://localhost:8080/WebServicePortafolio(27-11-2023)/NewWebService?WSDL')
        response = soap_client.call_method('listar_extras')

        extras = []
        
        if response:
            for extra in response:
                id_contrato_accidente=extra['id_contrato']

                if contrato['id_contrato_param'] == id_contrato_accidente:

                    fecha = extra['fecha_extra']
                    id_servicio = extra['id_servicio']
                    monto = extra['monto_extra']
                    tipo_extra = extra['tipo_servicio_desc']


                    extras.append({
                        'fecha':fecha,
                        'id_servicio':id_servicio,
                        'monto':monto,
                        'tipo_extra':tipo_extra
                    })



        return render(request, 'app/listarExtra.html',{'accidentes':extras})
    else:
        return redirect(login)
