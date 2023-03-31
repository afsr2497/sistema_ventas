from django.urls import path
from . import views

app_name = 'sistema_2'

urlpatterns = [
    path('',views.login_view,name='login_view'),
    path('log_out',views.log_out,name='log_out'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('ingresos',views.ingresos,name='ingresos'),
    path('egresos',views.egresos,name='egresos'),
    path('usuarios',views.usuarios,name='usuarios'),
    path('eliminar_usuario/<str:ind>',views.eliminar_usuario,name='eliminar_usuario'),
    path('actualizar_usuario/<str:ind>',views.actualizar_usuario,name='actualizar_usuario'),
    path('servicios',views.servicios,name='servicios'),
    path('eliminar_servicio/<str:ind>',views.eliminar_servicio,name='eliminar_servicio'),
    path('actualizar_servicio/<str:ind>',views.actualizar_servicio,name='actualizar_servicio'),
    path('importar_servicios',views.importar_servicios,name='importar_servicios'),
    path('clientes',views.clientes,name='clientes'),
    path('eliminar_cliente/<str:ind>',views.eliminar_cliente,name='eliminar_cliente'),
    path('actualizar_cliente/<str:ind>',views.actualizar_cliente,name='actualizar_cliente'),
    path('importar_clientes',views.importar_clientes,name='importar_clientes'),
    path('agregar_direcciones/<str:ind>',views.agregar_direcciones,name='agregar_direcciones'),
    path('productos',views.productos,name='productos'),
    path('eliminar_producto/<str:ind>',views.eliminar_producto,name='eliminar_producto'),
    path('actualizar_producto/<str:ind>',views.actualizar_producto,name='actualizar_producto'),
    path('importar_productos',views.importar_productos,name='importar_productos'),
    path('agregar_stock',views.agregar_stock,name='agregar_stock'),
    path('proformas',views.proformas,name='proformas'),
    path('crear_proforma',views.crear_proforma,name='crear_proforma'),
    path('eliminar_proforma/<str:ind>',views.eliminar_proforma,name='eliminar_proforma'),
    path('generar_guia/<str:ind>',views.generar_guia,name='generar_guia'),
    path('obtener_cliente/<str:ind>',views.obtener_cliente,name='obtener_cliente'),
    path('obtener_usuario/<str:ind>',views.obtener_usuario,name='obtener_usuario'),
    path('obtener_producto/<str:ind>',views.obtener_producto,name='obtener_producto'),
    path('obtener_servicio/<str:ind>',views.obtener_servicio,name='obtener_servicio'),
    path('agregar_proforma',views.agregar_proforma,name='agregar_proforma'),
    path('generar_guia/<str:ind>',views.generar_guia,name='generar_guia'),
    path('generar_factura/<str:ind>',views.generar_factura,name='generar_factura'),
    path('crear_factura/<str:ind>',views.crear_factura,name='crear_factura'),
    path('generar_boleta/<str:ind>',views.generar_boleta,name='generar_boleta'),
    path('crear_boleta/<str:ind>',views.crear_boleta,name='crear_boleta'),
    path('editar_proforma/<str:ind>',views.editar_proforma,name='editar_proforma'),
    path('editar_guia/<str:ind>',views.editar_guia,name='editar_guia'),
    path('editar_factura/<str:ind>',views.editar_factura,name='editar_factura'),
    path('editar_boleta/<str:ind>',views.editar_boleta,name='editar_boleta'),
    path('fact',views.fact,name='fact'),
    path('gui',views.gui,name='gui'),
    path('eliminar_guia/<str:ind>',views.eliminar_guia,name='eliminar_guia'),
    path('eliminar_factura/<str:ind>',views.eliminar_factura,name='eliminar_factura'),
    path('eliminar_boleta/<str:ind>',views.eliminar_boleta,name='eliminar_boleta'),
    path('bole',views.bole,name='bole'),
    path('descargar_proforma/<str:ind>',views.descargar_proforma,name='descargar_proforma'),
    path('descargar_guia/<str:ind>',views.descargar_guia,name='descargar_guia'),
    path('descargar_factura/<str:ind>',views.descargar_factura,name='descargar_factura'),
    path('descargar_boleta/<str:ind>',views.descargar_boleta,name='descargar_boleta'),
    path('enviar_factura/<str:ind>',views.enviar_factura,name='enviar_factura'),
    path('enviar_guia/<str:ind>',views.enviar_guia,name='enviar_guia'),
    path('enviar_boleta/<str:ind>',views.enviar_boleta,name='enviar_boleta'),
    path('configurar_documentos',views.configurar_documentos,name='configurar_documentos'),
    path('gen_guia_factura',views.gen_guia_factura,name='gen_guia_factura'),
    path('gen_guia_boleta',views.gen_guia_boleta,name='gen_guia_boleta'),
    path('gen_factura_cot/<str:ind>',views.gen_factura_cot,name='gen_factura_cot'),
    path('gen_boleta_cot/<str:ind>',views.gen_boleta_cot,name='gen_boleta_cot'),
    path('registros_bancarios',views.registros_bancarios,name='registros_bancarios'),
    path('notas_credito',views.notas_credito,name='notas_credito'),
    path('emitir_nota_factura/<str:ind>',views.emitir_nota_factura,name='emitir_nota_factura'),
    path('emitir_nota_boleta/<str:ind>',views.emitir_nota_boleta,name='emitir_nota_boleta'),
    path('descargar_nota_credito/<str:ind>',views.descargar_nota_credito,name='descargar_nota_credito'),
    path('enviar_nota_credito/<str:ind>',views.enviar_nota_credito,name='enviar_nota_credito'),
    path('eliminar_nota_credito/<str:ind>',views.eliminar_nota_credito,name='eliminar_nota_credito'),
    path('verificar_guia/<str:ind>',views.verificar_guia,name='verificar_guia'),
    path('gen_guia_cot/<str:ind>',views.gen_guia_cot,name='gen_guia_cot'),
    path('gen_factura_guia/<str:ind>',views.gen_factura_guia,name='gen_factura_guia'),
    path('gen_boleta_guia/<str:ind>',views.gen_boleta_guia,name='gen_boleta_guia'),
    path('crear_factura_guias',views.crear_factura_guias,name='crear_factura_guias'),
    path('crear_boleta_guias',views.crear_boleta_guias,name='crear_boleta_guias'),
    path('download_factura/<str:ind>',views.download_factura,name='download_factura'),
    path('download_guia/<str:ind>',views.download_guia,name='download_guia'),
    path('download_boleta/<str:ind>',views.download_boleta,name='download_boleta'),
    path('verificar_guia_teFacturo/<str:ind>',views.verificar_guia_teFacturo,name='verificar_guia_teFacturo'),
    path('verificar_factura_teFacturo/<str:ind>',views.verificar_factura_teFacturo,name='verificar_factura_teFacturo'),
    path('verificar_boleta_teFacturo/<str:ind>',views.verificar_boleta_teFacturo,name='verificar_boleta_teFacturo'),
    path('obtener_datos_ruc/<str:ind>',views.obtener_datos_ruc,name='objener_datos_ruc'),
    path('obtener_stock_producto/<str:ind>',views.obtener_stock_producto,name='obtener_stock_producto'),
    path('actualizar_info_producto/<str:ind>',views.actualizar_info_producto,name='obtener_info_producto'),
    path('eliminar_producto_tabla/<str:ind>',views.eliminar_producto_tabla,name='eliminar_producto_tabla'),
    path('update_producto/<str:ind>',views.update_producto,name='update_producto'),
    path('ver_movimientos/<str:ind>',views.ver_movimientos,name='ver_movimientos'),
    path('actualizar_cuenta/<str:ind>',views.actualizar_cuenta,name='actualizar_cuenta'),
    path('eliminar_cuenta/<str:ind>',views.eliminar_cuenta,name='eliminar_cuenta'),
    path('registrar_movimientos',views.importar_movimientos,name='importar_movimientos'),
    path('actualizar_mov/<str:ind>',views.actualizar_mov,name='actualizar_mov'),
    path('update_mov/<str:ind>',views.update_mov,name='update_mov'),
    path('obtener_facturas_cotizaciones_cliente/<str:ind>',views.obtener_facturas_cotizaciones_cliente,name='obtener_facturas_cliente'),
    path('obtener_guias_factura/<str:ind>',views.obtener_guias_factura,name='obtener_guias_factura'),
    path('exportar_todo',views.exportar_todo,name='exportar_todo'),
    path('descargar_filtrado',views.descargar_filtrado,name='descargar_filtrado'),
    path('comisiones',views.comisiones,name='comisiones'),
    path('eliminarTodo',views.eliminarTodo,name='eliminarTodo'),
    path('descargar_manual',views.descargar_manual,name='descargar_manual'),
    path('descargar_proforma_dolares/<str:ind>',views.descargar_proforma_dolares,name='descargar_proforma_dolares'),
    path('registro_abonos',views.registro_abonos,name='registro_abonos'),
    path('comprobar_abonos',views.comprobar_abonos,name='comprobar_abonos'),
    path('eliminar_abono/<str:ind>',views.eliminar_abono,name='eliminar_abono'),
    path('actualizar_abono/<str:ind>',views.actualizar_abono,name='actualizar_abono'),
    path('descargar_guia',views.descargar_guia,name='descargar_guia'),
    path('actualizar_roles/<str:ind>',views.actualizar_roles,name='actualizar_roles'),
    path('get_clients_statistics',views.get_clients_statistics,name='get_clients_statistics'),
    path('get_products_statistics',views.get_products_statistics,name='get_products_statistics'),
    path('get_vendedor_statistics',views.get_vendedor_statistics,name='get_vendedor_statistics'),
    path('get_ventas_meses/<str:ind>',views.get_ventas_meses,name='get_ventas_meses'),
    path('get_clientes_15',views.get_clientes_15,name='get_clientes_15'),
    path('get_productos_15',views.get_productos_15,name='get_productos_15'),
    path('get_ventas_tiempo_vendedor',views.get_ventas_tiempo_vendedor,name='get_ventas_tiempo_vendedor'),
    path('actualizar_precios_productos',views.actualizar_precios_productos,name='actualizar_precios_productos'),
    path('inventarios',views.inventarios,name='inventarios'),
    path('descargarInventario/<str:ind>',views.descargarInventario,name='descargarInventario'),
    path('aprobarInventario/<str:ind>',views.aprobarInventario,name='aprobarInventario'),
    path('observarInventario/<str:ind>',views.observarInventario,name='observarInventario'),
    path('eliminarInventario/<str:ind>',views.eliminarInventario,name='eliminarInventario'),
    path('emitir_nota_credito_factura/<str:ind>',views.emitir_nota_credito_factura,name='emitir_nota_credito_factura'),
    path('nuevoAlmacen',views.nuevoAlmacen,name='nuevoAlmacen'),
    path('eliminarAlmacen/<str:alm>',views.eliminarAlmancen,name='eliminarAlmacen'),
    path('get_productos_factura',views.get_productos_factura,name='get_productos_factura'),
    path('crear_nota_credito',views.crear_nota_credito,name='crear_nota_credito'),
    path('download_nota/<str:ind>',views.download_nota,name='download_nota'),
    path('almacenesSistema',views.almacenesSistema,name='almacenesSistema'),
    path('dashboard_clientes',views.dashboard_clientes,name='dashboard_clientes'),
    path('dashboard_productos',views.dashboard_productos,name='dashboard_productos'),
    path('dashboard_ventas',views.dashboard_ventas,name='dashboard_ventas'),
    path('agregarUbigeo',views.agregarUbigeo,name='agregarUbigeo'),
    path('eliminarUbigeo/<str:ind>',views.eliminarUbigeo,name='eliminarUbigeo'),
    path('cambiarAlmacen',views.cambiarAlmacen,name='cambiarAlmacen'),
    path('exportarKardex/<str:ind>',views.exportarKardex,name='exportarKardex'),
    path('actualizar_kpi',views.actualizar_kpi,name='actualizar_kpi'),
    path('actualizarInfoCliente/<str:ind>',views.actualizarInfoCliente,name='actualizarInfoCliente'),
    path('comprasMensuales/<str:ind>',views.comprasMensuales,name='comprasMensuales'),
    path('consultarDescuento',views.consultarDescuento,name='consultarDescuento'),
    path('actualizarDescuentoAlmacen/<str:almacen>',views.actualizarDescuentoAlmacen,name='actualizarDescuentoAlmacen'),
    path('emisionoc',views.emisionoc,name='emisionoc'),
    path('crear_orden',views.crear_orden,name='crear_orden'),
    path('descargar_orden/<str:ind>',views.descargarOrden,name='descargarOrden'),
    path('editarOrden/<str:ind>',views.editarOrden,name='editarOrden'),
    path('verificar_nota_teFacturo/<str:ind>',views.verificar_nota_teFacturo,name='verificar_nota_teFacturo'),
    path('getDatosAbono',views.getDatosAbono,name='getDatosAbono'),
    path('nuevoFormatoSoles/<str:ind>',views.nuevoFormatoSoles,name='nuevoFormatoSoles'),
    path('nuevoFormatoDolares/<str:ind>',views.nuevoFormatoDolares,name='nuevoFormatoDolares'),
    path('kits_productos',views.kits_productos,name='kits_productos'),
    path('exportarReporteVentas',views.exportarReporteVentas, name='exportarReporteVentas'),
    path('configComisiones',views.configComisiones,name='configComisiones'),
    path('eliminarConfiguracionComisiones/<str:ind>',views.eliminarConfiguracionComisiones,name='eliminarConfiguracionComisiones'),
    path('obtenerConfiguraciones/<str:ind>',views.obtenerConfiguraciones,name='obtenerConfiguraciones'),
]