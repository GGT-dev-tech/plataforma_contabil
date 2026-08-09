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
      // Hardcoded dummy empresa_id para fins de demonstração
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
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            Obras & Empreendimentos
          </h1>
          <p className="text-gray-400 mt-1">
            Gestão de centros de custo e patrimônio de afetação (RET).
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={handleSincronizar}
            className="px-4 py-2 bg-white/5 hover:bg-white/10 text-gray-300 border border-white/10 rounded-xl font-medium transition-all flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Sincronizar ERP
          </button>
          
          <button className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-xl font-medium transition-all shadow-lg shadow-primary-500/20 flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Nova Obra
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400">
          <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          Carregando obras...
        </div>
      ) : obras.length === 0 ? (
        <div className="text-center py-12 glass-panel rounded-2xl border border-white/5">
          <Building2 className="w-12 h-12 text-gray-500 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium text-gray-300">Nenhuma obra cadastrada</h3>
          <p className="text-gray-500 mt-2">Você ainda não possui empreendimentos registrados.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {obras.map((obra) => (
            <div key={obra.id} className="glass-panel rounded-2xl p-6 border border-white/5 hover:border-primary-500/30 transition-all group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary-500/5 rounded-full blur-2xl -mr-16 -mt-16 group-hover:bg-primary-500/10 transition-all"></div>
              
              <div className="flex justify-between items-start mb-4 relative z-10">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-primary-400">
                    <HardHat className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-100">{obra.nome}</h3>
                    <p className="text-xs text-gray-500">{obra.codigo_interno || 'Sem Cód.'} • CNO: {obra.codigo_cno || 'Não inf.'}</p>
                  </div>
                </div>
              </div>

              <div className="space-y-3 mb-6 relative z-10">
                <div className="flex items-center text-sm text-gray-400">
                  <MapPin className="w-4 h-4 mr-2 opacity-70" />
                  {obra.municipio_nome || 'Local não informado'} - {obra.uf || ''}
                </div>
                <div className="flex items-center text-sm text-gray-400">
                  <ReceiptText className="w-4 h-4 mr-2 opacity-70" />
                  Regime: <span className="ml-1 text-gray-200 font-medium">{obra.regime_tributario}</span>
                  {obra.patrimonio_afetacao && <span className="ml-2 px-2 py-0.5 bg-accent-500/20 text-accent-400 text-[10px] rounded-full border border-accent-500/30 font-bold">RET</span>}
                </div>
              </div>

              <div className="relative z-10 pt-4 border-t border-white/10">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs text-gray-400 flex items-center gap-1"><Percent className="w-3 h-3" /> Avanço Físico (POC)</span>
                  <span className="text-sm font-bold text-gray-200">{obra.percentual_avanco_fisico}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5 mt-2">
                  <div 
                    className="bg-gradient-to-r from-primary-500 to-accent-500 h-1.5 rounded-full" 
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
