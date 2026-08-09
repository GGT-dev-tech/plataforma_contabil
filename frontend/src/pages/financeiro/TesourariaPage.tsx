import React, { useEffect, useState } from 'react';
import { Landmark, ArrowUpRight, ArrowDownRight, Plus, Search, DollarSign } from 'lucide-react';
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
      const token = localStorage.getItem('@App:token');
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
    const [year, month, day] = dateStr.split('-');
    return `${day}/${month}/${year}`;
  };

  const saldoTotal = contas.reduce((acc, c) => acc + c.saldo_atual, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 flex items-center gap-3">
            <Landmark className="w-8 h-8 text-primary-400" />
            Contas & Dinheiro (Tesouraria)
          </h1>
          <p className="text-gray-400 mt-1">
            Gestão de saldos de caixa, contas correntes e conciliação bancária.
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-xl font-medium transition-all flex items-center gap-2 border border-white/10">
            Importar OFX
          </button>
          <button className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-xl font-medium transition-all shadow-[0_0_20px_rgba(37,99,235,0.2)] flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Nova Transação
          </button>
        </div>
      </div>

      {!activeWorkspace ? (
        <div className="flex-1 flex items-center justify-center border border-white/10 rounded-2xl p-10 bg-white/5">
          <p className="text-gray-400">Selecione uma Empresa no menu de configurações.</p>
        </div>
      ) : loading && contas.length === 0 ? (
        <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mt-10"></div>
      ) : (
        <>
          {/* Dashboard Resumo */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white/5 border border-white/10 p-6 rounded-2xl relative overflow-hidden group">
              <div className="absolute -right-4 -top-4 w-24 h-24 bg-primary-500/10 rounded-full blur-2xl group-hover:bg-primary-500/20 transition-all"></div>
              <p className="text-sm text-gray-400 font-medium mb-1">Saldo Consolidado Total</p>
              <h2 className="text-3xl font-bold text-white mb-2">{formatCurrency(saldoTotal)}</h2>
            </div>
            
            {contas.map(conta => (
              <div key={conta.id} className="bg-white/5 border border-white/10 p-6 rounded-2xl relative overflow-hidden hover:border-white/20 transition-all cursor-pointer">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-gray-200">{conta.descricao}</h3>
                    <p className="text-xs text-gray-400 font-mono mt-1">{conta.banco} - Ag: {conta.agencia || '-'} / CC: {conta.conta || '-'}</p>
                  </div>
                  <div className="p-2 bg-white/5 rounded-lg">
                    <Landmark className="w-5 h-5 text-gray-400" />
                  </div>
                </div>
                <h4 className={`text-2xl font-bold ${conta.saldo_atual >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {formatCurrency(conta.saldo_atual)}
                </h4>
              </div>
            ))}
            
            {contas.length === 0 && (
              <div className="bg-white/5 border border-white/10 p-6 rounded-2xl flex items-center justify-center border-dashed cursor-pointer hover:bg-white/10 transition-all">
                <div className="text-center text-gray-400 flex flex-col items-center gap-2">
                  <Plus className="w-6 h-6" />
                  <span className="text-sm font-bold">Cadastrar Conta Corrente</span>
                </div>
              </div>
            )}
          </div>

          {/* Extrato Bancário */}
          <div className="bg-[#1C1C1C] rounded-2xl border border-white/10 overflow-hidden shadow-xl mt-6">
            <div className="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Search className="w-5 h-5 text-gray-400" /> Extrato de Transações
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-black/20 text-gray-400 text-xs uppercase tracking-wider">
                    <th className="p-4 font-semibold w-32">Data</th>
                    <th className="p-4 font-semibold">Conta</th>
                    <th className="p-4 font-semibold">Descrição</th>
                    <th className="p-4 font-semibold w-32 text-right">Valor</th>
                    <th className="p-4 font-semibold w-24 text-center">Tipo</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {transacoes.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="p-8 text-center text-gray-500">
                        Nenhuma transação registrada.
                      </td>
                    </tr>
                  ) : transacoes.map(t => (
                    <tr key={t.id} className="hover:bg-white/5 transition-colors">
                      <td className="p-4 text-gray-300 text-sm">{formatDate(t.data_transacao)}</td>
                      <td className="p-4 text-gray-300 font-medium">{t.conta_descricao}</td>
                      <td className="p-4 text-gray-300">{t.descricao}</td>
                      <td className={`p-4 text-right font-bold ${t.tipo === 'ENTRADA' ? 'text-emerald-400' : 'text-red-400'}`}>
                        {t.tipo === 'ENTRADA' ? '+' : '-'}{formatCurrency(t.valor)}
                      </td>
                      <td className="p-4 text-center">
                        <div className={`inline-flex items-center justify-center p-1.5 rounded-lg ${t.tipo === 'ENTRADA' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
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
