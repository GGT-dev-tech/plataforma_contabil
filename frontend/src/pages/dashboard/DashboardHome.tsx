import React, { useEffect, useState } from 'react';
import { LineChart, LayoutDashboard, Wallet, TrendingUp, Building2, CheckCircle2 } from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

interface DashboardDados {
  saldo_consolidado: number;
  total_receitas: number;
  total_despesas: number;
  vgv_aprovado: number;
  lucro_operacional: number;
}

export const DashboardHome: React.FC = () => {
  const { activeWorkspace } = useWorkspace();
  const [dados, setDados] = useState<DashboardDados | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchData = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/v1/analytics/dashboard', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          setDados(await res.json());
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [activeWorkspace]);

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <LayoutDashboard className="w-8 h-8 text-primary-600" />
            Centro de Comando
          </h1>
          <p className="text-slate-500 mt-1">
            Visão consolidada da operação, liquidez e resultado operacional.
          </p>
        </div>
      </div>

      {!activeWorkspace ? (
        <div className="p-12 border border-slate-200 rounded-xl bg-white shadow-sm text-center text-slate-500">
          Selecione uma Empresa no menu de topo para ver os dados operacionais.
        </div>
      ) : loading || !dados ? (
        <div className="flex justify-center p-12">
          <div className="animate-spin w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full"></div>
        </div>
      ) : (
        <>
          {/* Top Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
              <div className="flex items-center gap-2 text-primary-600 mb-2">
                <Wallet className="w-5 h-5" />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Saldo em Caixa</span>
              </div>
              <h2 className="text-3xl font-bold text-slate-800">{formatCurrency(dados.saldo_consolidado)}</h2>
            </div>
            
            <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
              <div className="flex items-center gap-2 text-emerald-600 mb-2">
                <CheckCircle2 className="w-5 h-5" />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">VGV Aprovado</span>
              </div>
              <h2 className="text-3xl font-bold text-slate-800">{formatCurrency(dados.vgv_aprovado)}</h2>
              <p className="text-xs text-slate-500 mt-1">Vendas aprovadas no CRM</p>
            </div>

            <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
              <div className="flex items-center gap-2 text-indigo-600 mb-2">
                <TrendingUp className="w-5 h-5" />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Resultado Operacional</span>
              </div>
              <h2 className={`text-3xl font-bold ${dados.lucro_operacional >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                {formatCurrency(dados.lucro_operacional)}
              </h2>
            </div>
            
            <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
              <div className="flex items-center gap-2 text-amber-600 mb-2">
                <Building2 className="w-5 h-5" />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Receitas vs Despesas</span>
              </div>
              <div className="flex justify-between items-end mt-1">
                <div>
                  <p className="text-[10px] text-slate-400 uppercase font-bold">Receitas</p>
                  <p className="font-bold text-emerald-600">{formatCurrency(dados.total_receitas)}</p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-slate-400 uppercase font-bold">Despesas</p>
                  <p className="font-bold text-red-600">{formatCurrency(dados.total_despesas)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Gráfico Visual */}
          <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm mt-6">
            <h3 className="text-base font-bold text-slate-800 mb-6 flex items-center gap-2">
              <LineChart className="w-5 h-5 text-slate-500" /> Comparativo Financeiro
            </h3>
            
            <div className="flex items-end gap-8 h-64 max-w-2xl mx-auto pb-6 border-b border-slate-200 relative">
              <div className="absolute inset-0 flex flex-col justify-between pointer-events-none">
                <div className="w-full h-[1px] bg-slate-100"></div>
                <div className="w-full h-[1px] bg-slate-100"></div>
                <div className="w-full h-[1px] bg-slate-100"></div>
                <div className="w-full h-[1px] bg-slate-100"></div>
              </div>

              {/* Bar 1: Receitas */}
              <div className="flex-1 flex flex-col items-center justify-end h-full z-10 group">
                <div className="text-emerald-600 font-bold text-sm mb-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {formatCurrency(dados.total_receitas)}
                </div>
                <div 
                  className="w-24 bg-emerald-500 rounded-t-lg transition-all duration-700"
                  style={{ height: dados.total_receitas > 0 ? '80%' : '10%' }}
                ></div>
                <p className="mt-4 text-xs font-semibold text-slate-600">Receitas Totais</p>
              </div>

              {/* Bar 2: Despesas */}
              <div className="flex-1 flex flex-col items-center justify-end h-full z-10 group">
                <div className="text-red-600 font-bold text-sm mb-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {formatCurrency(dados.total_despesas)}
                </div>
                <div 
                  className="w-24 bg-red-500 rounded-t-lg transition-all duration-700"
                  style={{ height: dados.total_despesas > 0 ? (dados.total_despesas > dados.total_receitas ? '90%' : '50%') : '10%' }}
                ></div>
                <p className="mt-4 text-xs font-semibold text-slate-600">Despesas Totais</p>
              </div>
            </div>
            <p className="text-center text-xs text-slate-400 mt-4">Passe o mouse sobre as barras para ver os valores exatos.</p>
          </div>
        </>
      )}
    </div>
  );
};
