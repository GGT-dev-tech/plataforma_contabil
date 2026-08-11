import React, { useEffect, useState } from 'react';
import { Building2, Plus, Percent, MapPin, ReceiptText, HardHat, RefreshCw } from 'lucide-react';
import { getObras, Obra, sincronizarObras } from '../../services/api/obras';

export const ObrasPage: React.FC = () => {
  const [obras, setObras] = useState<Obra[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchObras();
  }, []);

  const fetchObras = async () => {
    try {
      setLoading(true);
      const data = await getObras();
      setObras(data);
    } catch (error) {
      console.error('Failed to fetch obras', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSincronizar = async () => {
    try {
      setLoading(true);
      const res = await sincronizarObras("32ecbd0c-25d2-43bb-a30f-b1eaf602ed05", "sienge");
      alert(`Sincronização concluída! ${res.novas_obras_importadas} novas obras importadas.`);
      await fetchObras();
    } catch (error) {
      console.error('Failed to sync obras', error);
      alert('Erro ao sincronizar com o ERP Sienge.');
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <Building2 className="w-8 h-8 text-primary-600" />
            Obras & Centros de Custo
          </h1>
          <p className="text-slate-500 mt-1">
            Gestão de empreendimentos, avanço físico e patrimônio de afetação (RET).
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={handleSincronizar}
            className="px-4 py-2 bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg font-medium text-sm transition-colors flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
            Sincronizar ERP
          </button>
          
          <button className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Nova Obra
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-500 flex flex-col items-center">
          <div className="animate-spin w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full mb-3"></div>
          Carregando obras...
        </div>
      ) : obras.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-slate-200 shadow-sm p-8">
          <Building2 className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-700 mb-1">Nenhuma obra cadastrada</h3>
          <p className="text-slate-500 text-sm">Você ainda não possui empreendimentos registrados.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {obras.map((obra) => (
            <div key={obra.id} className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:border-primary-500 transition-all group">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary-50 border border-primary-100 flex items-center justify-center text-primary-600">
                    <HardHat className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-800">{obra.nome}</h3>
                    <p className="text-xs text-slate-500">{obra.codigo_interno || 'Sem Cód.'} • CNO: {obra.codigo_cno || 'Não inf.'}</p>
                  </div>
                </div>
              </div>

              <div className="space-y-3 mb-6">
                <div className="flex items-center text-sm text-slate-600">
                  <MapPin className="w-4 h-4 mr-2 text-slate-400" />
                  {obra.municipio_nome || 'Local não informado'} - {obra.uf || ''}
                </div>
                <div className="flex items-center text-sm text-slate-600">
                  <ReceiptText className="w-4 h-4 mr-2 text-slate-400" />
                  Regime: <span className="ml-1 text-slate-800 font-semibold">{obra.regime_tributario}</span>
                  {obra.patrimonio_afetacao && <span className="ml-2 px-2 py-0.5 bg-amber-50 text-amber-700 text-xs rounded border border-amber-200 font-bold">RET</span>}
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs text-slate-500 font-semibold flex items-center gap-1"><Percent className="w-3 h-3 text-slate-400" /> Avanço Físico (POC)</span>
                  <span className="text-sm font-bold text-slate-800">{obra.percentual_avanco_fisico}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 mt-2 overflow-hidden">
                  <div 
                    className="bg-primary-600 h-2 rounded-full transition-all" 
                    style={{ width: `${Math.min(100, Math.max(0, obra.percentual_avanco_fisico))}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
