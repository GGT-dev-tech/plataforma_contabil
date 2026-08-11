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
      const token = localStorage.getItem('token');
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
      const token = localStorage.getItem('token');
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

  const renderCol = (title: string, status: string, icon: React.ReactNode, badgeClass: string, nextStatus?: string) => {
    const cols = propostas.filter(p => p.status === status);
    return (
      <div className="flex flex-col flex-1 min-w-[300px]">
        <div className="flex items-center justify-between p-4 mb-4 rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center gap-2 font-bold text-slate-800">
            {icon}
            {title}
          </div>
          <div className="px-2.5 py-0.5 bg-slate-100 border border-slate-200 text-slate-700 rounded-full text-xs font-bold">
            {cols.length}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto space-y-3 pr-2 pb-4">
          {cols.length === 0 ? (
            <div className="text-center p-6 border border-dashed border-slate-200 rounded-xl bg-white text-slate-400 text-sm">
              Nenhuma proposta
            </div>
          ) : (
            cols.map(p => (
              <div key={p.id} className="p-4 rounded-xl border border-slate-200 shadow-sm bg-white hover:border-primary-500 transition-all">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-slate-800 truncate">{p.cliente_nome}</h4>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${badgeClass}`}>
                    {p.status.replace('_', ' ')}
                  </span>
                </div>
                
                <p className="text-xs text-slate-500 mt-1">
                  Unidade: <strong className="text-slate-700">{p.unidade_descricao || 'N/A'}</strong>
                </p>
                
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-end justify-between">
                  <div>
                    <p className="text-[10px] uppercase font-bold tracking-wider text-slate-400">VGV Negociado</p>
                    <p className="font-bold text-primary-600">
                      {formatCurrency(p.valor_negociado)}
                    </p>
                  </div>
                </div>

                {nextStatus && (
                  <div className="mt-4 pt-3 border-t border-slate-100 flex gap-2">
                    <button 
                      onClick={() => handleUpdateStatus(p.id, nextStatus)}
                      className="flex-1 py-1.5 rounded-lg text-xs font-semibold bg-primary-50 text-primary-700 hover:bg-primary-100 border border-primary-200 transition-colors"
                    >
                      Avançar para {nextStatus.replace('_', ' ')}
                    </button>
                    {status === 'EM_ANALISE' && (
                      <button 
                        onClick={() => handleUpdateStatus(p.id, 'PERDIDA')}
                        className="px-3 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 rounded-lg text-xs font-semibold transition-colors"
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
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <Users className="w-8 h-8 text-primary-600" />
            CRM & Comercial
          </h1>
          <p className="text-slate-500 mt-1">
            Funil de vendas, acompanhamento de propostas e contratos de unidades.
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
            <Search className="w-4 h-4 text-slate-400" />
            Buscar Cliente
          </button>
          <button className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Nova Proposta
          </button>
        </div>
      </div>

      {!activeWorkspace ? (
        <div className="p-12 text-center border border-slate-200 rounded-xl bg-white shadow-sm">
          <AlertCircle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-800 mb-1">Selecione uma Empresa</h3>
          <p className="text-slate-500 text-sm">Selecione um workspace ativo no menu de topo para visualizar o CRM.</p>
        </div>
      ) : loading && propostas.length === 0 ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full mx-auto"></div>
        </div>
      ) : (
        <div className="overflow-x-auto pb-4">
          <div className="flex gap-6 min-w-max">
            {renderCol('Nova Proposta', 'NOVA', <Plus className="w-5 h-5 text-blue-600" />, 'bg-blue-50 text-blue-700 border border-blue-200', 'EM_ANALISE')}
            {renderCol('Em Análise', 'EM_ANALISE', <FileSignature className="w-5 h-5 text-purple-600" />, 'bg-purple-50 text-purple-700 border border-purple-200', 'APROVADA')}
            {renderCol('Venda Aprovada', 'APROVADA', <CheckCircle2 className="w-5 h-5 text-emerald-600" />, 'bg-emerald-50 text-emerald-700 border border-emerald-200')}
            {renderCol('Perdida', 'PERDIDA', <XCircle className="w-5 h-5 text-red-600" />, 'bg-red-50 text-red-700 border border-red-200')}
          </div>
        </div>
      )}
    </div>
  );
};
