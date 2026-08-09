import React, { useEffect, useState } from 'react';
import { Landmark, AlertCircle, Plus, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

interface Titulo {
  id: string;
  tipo: 'PAGAR' | 'RECEBER';
  status: 'ABERTO' | 'PAGO' | 'ATRASADO' | 'CANCELADO';
  descricao: string;
  fornecedor_cliente_nome: string;
  valor_nominal: number;
  data_vencimento: string;
  gerado_automaticamente: boolean;
}

export const ReceitasDespesasPage: React.FC = () => {
  const { activeWorkspace } = useWorkspace();
  const [titulos, setTitulos] = useState<Titulo[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterTipo, setFilterTipo] = useState<'ALL' | 'PAGAR' | 'RECEBER'>('ALL');

  const fetchTitulos = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/financeiro/titulos?empresa_id=${activeWorkspace.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Erro ao buscar títulos');
      const data = await response.json();
      setTitulos(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTitulos();
  }, [activeWorkspace]);

  const handlePagar = async (id: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/financeiro/titulos/${id}/status`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          status: 'PAGO',
          data_pagamento: new Date().toISOString().split('T')[0]
        })
      });
      if (!response.ok) throw new Error('Erro ao pagar título');
      fetchTitulos();
    } catch (error) {
      console.error(error);
      alert('Erro ao processar pagamento');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  };

  const formatDate = (dateString: string) => {
    const d = new Date(dateString);
    // adjust for timezone issues, simple split is safer for YYYY-MM-DD
    const parts = dateString.split('-');
    if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`;
    return d.toLocaleDateString('pt-BR');
  };

  const isVencido = (dataStr: string, status: string) => {
    if (status === 'PAGO' || status === 'CANCELADO') return false;
    const today = new Date().toISOString().split('T')[0];
    return dataStr < today;
  };

  const filteredTitulos = titulos.filter(t => filterTipo === 'ALL' || t.tipo === filterTipo);

  const renderCol = (title: string, status: string, icon: React.ReactNode, colorClass: string) => {
    const cols = filteredTitulos.filter(t => t.status === status);
    return (
      <div className="flex flex-col flex-1 min-w-[300px]">
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
              Nenhum título
            </div>
          ) : (
            cols.map(t => (
              <div key={t.id} className={`p-4 rounded-xl border shadow-lg transition-all ${
                t.tipo === 'PAGAR' ? 'bg-red-500/5 border-red-500/20' : 'bg-emerald-500/5 border-emerald-500/20'
              }`}>
                <div className="flex justify-between items-start mb-2">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-widest ${
                    t.tipo === 'PAGAR' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {t.tipo}
                  </span>
                  {t.gerado_automaticamente && (
                    <span className="text-[10px] text-primary-400 bg-primary-500/10 px-2 py-0.5 rounded-full" title="Gerado via Retenção (Documento Fiscal)">
                      Automático
                    </span>
                  )}
                </div>
                
                <h4 className="font-semibold text-gray-200 line-clamp-2 leading-tight" title={t.descricao}>
                  {t.descricao}
                </h4>
                <p className="text-xs text-gray-500 mt-1 truncate">{t.fornecedor_cliente_nome || 'S/N'}</p>
                
                <div className="mt-4 flex items-end justify-between">
                  <div>
                    <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Valor</p>
                    <p className={`font-bold ${t.tipo === 'PAGAR' ? 'text-red-400' : 'text-emerald-400'}`}>
                      {formatCurrency(t.valor_nominal)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Vencimento</p>
                    <p className={`text-sm font-medium ${isVencido(t.data_vencimento, t.status) ? 'text-red-500' : 'text-gray-300'}`}>
                      {formatDate(t.data_vencimento)}
                    </p>
                  </div>
                </div>

                {t.status === 'ABERTO' && (
                  <div className="mt-4 pt-3 border-t border-white/5 flex gap-2">
                    <button 
                      onClick={() => handlePagar(t.id)}
                      className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all ${
                        t.tipo === 'PAGAR' 
                          ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30' 
                          : 'bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30'
                      }`}
                    >
                      {t.tipo === 'PAGAR' ? 'Marcar como Pago' : 'Marcar como Recebido'}
                    </button>
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
            <Landmark className="w-8 h-8 text-primary-400" />
            Receitas & Despesas
          </h1>
          <p className="text-gray-400 mt-1">
            Gestão Financeira integrada ao contas a pagar e receber da construtora.
          </p>
        </div>
        
        <div className="flex items-center gap-2 bg-white/5 p-1 rounded-xl border border-white/10">
          {(['ALL', 'PAGAR', 'RECEBER'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilterTipo(f)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                filterTipo === f 
                  ? 'bg-primary-500 text-white shadow-lg' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {f === 'ALL' ? 'Todos' : f === 'PAGAR' ? 'A Pagar' : 'A Receber'}
            </button>
          ))}
        </div>
      </div>

      {!activeWorkspace ? (
        <div className="flex-1 flex items-center justify-center border border-white/10 rounded-2xl bg-white/5">
          <div className="text-center max-w-sm">
            <AlertCircle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Selecione uma Empresa</h3>
            <p className="text-gray-400">Você precisa selecionar um workspace ativo no menu de configurações para visualizar o financeiro.</p>
          </div>
        </div>
      ) : loading && titulos.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full"></div>
        </div>
      ) : (
        <div className="flex-1 overflow-x-auto overflow-y-hidden">
          <div className="flex gap-6 h-full min-w-max pb-4">
            {renderCol('Em Aberto', 'ABERTO', <Clock className="w-5 h-5" />, 'bg-blue-500/10 text-blue-400')}
            {renderCol('Pagos / Recebidos', 'PAGO', <CheckCircle2 className="w-5 h-5" />, 'bg-emerald-500/10 text-emerald-400')}
            {renderCol('Atrasados', 'ATRASADO', <AlertCircle className="w-5 h-5" />, 'bg-orange-500/10 text-orange-400')}
            {renderCol('Cancelados', 'CANCELADO', <XCircle className="w-5 h-5" />, 'bg-gray-500/10 text-gray-400')}
          </div>
        </div>
      )}
    </div>
  );
};
