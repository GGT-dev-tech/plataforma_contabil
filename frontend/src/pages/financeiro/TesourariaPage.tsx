import React, { useEffect, useState } from 'react';
import { Landmark, ArrowUpRight, ArrowDownRight, Plus, Search } from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

interface ContaBancaria {
  id: string;
  banco: string;
  agencia: string;
  conta: string;
  descricao: string;
  saldo_atual: number;
}

interface Transacao {
  id: string;
  conta_bancaria_id: string;
  conta_descricao: string;
  data_transacao: string;
  tipo: 'ENTRADA' | 'SAIDA';
  valor: number;
  descricao: string;
}

export const TesourariaPage: React.FC = () => {
  const { activeWorkspace } = useWorkspace();
  const [contas, setContas] = useState<ContaBancaria[]>([]);
  const [transacoes, setTransacoes] = useState<Transacao[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchDados = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };
      
      const [contasRes, transacoesRes] = await Promise.all([
        fetch('/api/v1/tesouraria/contas', { headers }),
        fetch('/api/v1/tesouraria/transacoes', { headers })
      ]);

      if (contasRes.ok) setContas(await contasRes.json());
      if (transacoesRes.ok) setTransacoes(await transacoesRes.json());
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDados();
  }, [activeWorkspace]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  };

  const formatDate = (dateStr: string) => {
    const parts = dateStr.split('-');
    if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`;
    return dateStr;
  };

  const saldoTotal = contas.reduce((acc, c) => acc + c.saldo_atual, 0);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <Landmark className="w-8 h-8 text-primary-600" />
            Contas & Tesouraria
          </h1>
          <p className="text-slate-500 mt-1">
            Gestão de saldos de caixa, contas correntes e extratos bancários.
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg text-sm font-medium transition-colors">
            Importar OFX
          </button>
          <button className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Nova Transação
          </button>
        </div>
      </div>

      {!activeWorkspace ? (
        <div className="p-12 text-center border border-slate-200 rounded-xl bg-white shadow-sm">
          <p className="text-slate-500">Selecione uma Empresa no menu de topo para visualizar a tesouraria.</p>
        </div>
      ) : loading && contas.length === 0 ? (
        <div className="animate-spin w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full mx-auto mt-10"></div>
      ) : (
        <>
          {/* Dashboard Resumo */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
              <p className="text-xs uppercase font-bold tracking-wider text-slate-400 mb-1">Saldo Consolidado Total</p>
              <h2 className="text-3xl font-bold text-slate-800">{formatCurrency(saldoTotal)}</h2>
            </div>
            
            {contas.map(conta => (
              <div key={conta.id} className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm hover:border-primary-500 transition-all cursor-pointer">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-slate-800">{conta.descricao}</h3>
                    <p className="text-xs text-slate-500 font-mono mt-1">{conta.banco} - Ag: {conta.agencia || '-'} / CC: {conta.conta || '-'}</p>
                  </div>
                  <div className="p-2 bg-slate-100 rounded-lg">
                    <Landmark className="w-5 h-5 text-slate-500" />
                  </div>
                </div>
                <h4 className={`text-2xl font-bold ${conta.saldo_atual >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                  {formatCurrency(conta.saldo_atual)}
                </h4>
              </div>
            ))}
            
            {contas.length === 0 && (
              <div className="bg-white border-2 border-dashed border-slate-200 p-6 rounded-xl flex items-center justify-center cursor-pointer hover:bg-slate-50 transition-all">
                <div className="text-center text-slate-500 flex flex-col items-center gap-2">
                  <Plus className="w-6 h-6 text-slate-400" />
                  <span className="text-sm font-bold text-slate-700">Cadastrar Conta Corrente</span>
                </div>
              </div>
            )}
          </div>

          {/* Extrato Bancário */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm mt-6">
            <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
              <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
                <Search className="w-4 h-4 text-slate-500" /> Extrato de Transações
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider border-b border-slate-200">
                    <th className="p-4 font-semibold w-32">Data</th>
                    <th className="p-4 font-semibold">Conta</th>
                    <th className="p-4 font-semibold">Descrição</th>
                    <th className="p-4 font-semibold w-32 text-right">Valor</th>
                    <th className="p-4 font-semibold w-24 text-center">Tipo</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {transacoes.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="p-8 text-center text-slate-500">
                        Nenhuma transação registrada.
                      </td>
                    </tr>
                  ) : transacoes.map(t => (
                    <tr key={t.id} className="hover:bg-slate-50 transition-colors">
                      <td className="p-4 text-slate-600">{formatDate(t.data_transacao)}</td>
                      <td className="p-4 text-slate-800 font-medium">{t.conta_descricao}</td>
                      <td className="p-4 text-slate-700">{t.descricao}</td>
                      <td className={`p-4 text-right font-bold ${t.tipo === 'ENTRADA' ? 'text-emerald-600' : 'text-red-600'}`}>
                        {t.tipo === 'ENTRADA' ? '+' : '-'}{formatCurrency(t.valor)}
                      </td>
                      <td className="p-4 text-center">
                        <div className={`inline-flex items-center justify-center p-1.5 rounded-lg ${t.tipo === 'ENTRADA' ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'}`}>
                          {t.tipo === 'ENTRADA' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
