import React, { useEffect, useState } from 'react';
import { Users, AlertCircle, Plus, FileSignature, CheckCircle2, XCircle, Search } from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

interface Proposta {
  id: string;
  cliente_nome: string;
  valor_negociado: number;
  unidade_descricao: string;
  status: 'NOVA' | 'EM_ANALISE' | 'APROVADA' | 'PERDIDA';
  data_proposta: string;
}

export const CrmPage: React.FC = () => {
  const { activeWorkspace } = useWorkspace();
  const [propostas, setPropostas] = useState<Proposta[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchPropostas = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('@App:token');
      const response = await fetch(`/api/v1/crm/propostas`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Erro ao buscar propostas');
      const data = await response.json();
      setPropostas(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPropostas();
  }, [activeWorkspace]);

  const handleUpdateStatus = async (id: string, newStatus: string) => {
    try {
      const token = localStorage.getItem('@App:token');
      const response = await fetch(`/api/v1/crm/propostas/${id}/status`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });
      if (!response.ok) throw new Error('Erro ao atualizar proposta');
      fetchPropostas();
    } catch (error) {
      console.error(error);
      alert('Erro ao processar status');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  };

  const renderCol = (title: string, status: string, icon: React.ReactNode, colorClass: string, nextStatus?: string) => {
    const cols = propostas.filter(p => p.status === status);
    return (
      <div className="flex flex-col flex-1 min-w-[320px]">
        <div className={`flex items-center justify-between p-4 mb-4 rounded-xl border border-white/10 ${colorClass}`}>
          <div className="flex items-center gap-2 font-semibold">
            {icon}
            {title}
          </div>
          <div className="px-2 py-0.5 bg-black/20 rounded-full text-xs font-bold">
            {cols.length}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto space-y-3 custom-scrollbar pr-2 pb-4">
          {cols.length === 0 ? (
            <div className="text-center p-6 border border-dashed border-white/10 rounded-xl text-gray-500 text-sm">
              Nenhuma proposta
            </div>
          ) : (
            cols.map(p => (
              <div key={p.id} className="p-4 rounded-xl border shadow-lg transition-all bg-white/5 border-white/10 hover:border-white/20 group">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold text-gray-200 line-clamp-1">{p.cliente_nome}</h4>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-widest ${colorClass.replace('bg-', 'bg-').replace('/10', '/20')}`}>
                    {p.status.replace('_', ' ')}
                  </span>
                </div>
                
                <p className="text-xs text-gray-400 mt-1 flex items-center gap-1">
                  Unidade: <strong className="text-gray-300">{p.unidade_descricao || 'N/A'}</strong>
                </p>
                
                <div className="mt-4 pt-3 border-t border-white/5 flex items-end justify-between">
                  <div>
                    <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">VGV Negociado</p>
                    <p className="font-bold text-primary-400">
                      {formatCurrency(p.valor_negociado)}
                    </p>
                  </div>
                </div>

                {nextStatus && (
                  <div className="mt-4 pt-3 border-t border-white/5 flex gap-2">
                    <button 
                      onClick={() => handleUpdateStatus(p.id, nextStatus)}
                      className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all ${colorClass.replace('/10', '/20')} hover:brightness-125`}
                    >
                      Avançar para {nextStatus.replace('_', ' ')}
                    </button>
                    {status === 'EM_ANALISE' && (
                      <button 
                        onClick={() => handleUpdateStatus(p.id, 'PERDIDA')}
                        className="px-3 py-1.5 bg-red-500/20 text-red-300 rounded-lg text-xs font-bold transition-all hover:bg-red-500/30"
                      >
                        Perdida
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 h-[calc(100vh-140px)] flex flex-col">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 flex-shrink-0">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 flex items-center gap-3">
            <Users className="w-8 h-8 text-primary-400" />
            CRM & Vendas
          </h1>
          <p className="text-gray-400 mt-1">
            Gestão do funil de vendas, clientes e propostas de unidades.
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-xl font-medium transition-all flex items-center gap-2 border border-white/10">
            <Search className="w-4 h-4" />
            Buscar Cliente
          </button>
          <button className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-xl font-medium transition-all shadow-[0_0_20px_rgba(37,99,235,0.2)] flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Nova Proposta
          </button>
        </div>
      </div>

      {!activeWorkspace ? (
        <div className="flex-1 flex items-center justify-center border border-white/10 rounded-2xl bg-white/5">
          <div className="text-center max-w-sm">
            <AlertCircle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Selecione uma Empresa</h3>
            <p className="text-gray-400">Você precisa selecionar um workspace ativo no menu de configurações para visualizar o CRM.</p>
          </div>
        </div>
      ) : loading && propostas.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full"></div>
        </div>
      ) : (
        <div className="flex-1 overflow-x-auto overflow-y-hidden mt-4">
          <div className="flex gap-6 h-full min-w-max pb-4">
            {renderCol('Nova Proposta', 'NOVA', <Plus className="w-5 h-5" />, 'bg-blue-500/10 text-blue-400', 'EM_ANALISE')}
            {renderCol('Em Análise', 'EM_ANALISE', <FileSignature className="w-5 h-5" />, 'bg-purple-500/10 text-purple-400', 'APROVADA')}
            {renderCol('Venda Aprovada', 'APROVADA', <CheckCircle2 className="w-5 h-5" />, 'bg-emerald-500/10 text-emerald-400')}
            {renderCol('Perdida', 'PERDIDA', <XCircle className="w-5 h-5" />, 'bg-red-500/10 text-red-400')}
          </div>
        </div>
      )}
    </div>
  );
};
