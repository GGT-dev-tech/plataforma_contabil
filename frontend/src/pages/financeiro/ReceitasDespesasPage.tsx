import React, { useEffect, useState, useCallback } from 'react';
import { Landmark, Download, Calendar, RefreshCw, AlertCircle, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';
import { apiClient as api } from '../../services/api';

interface DreData {
  RECEITA_BRUTA?: number;
  DEDUCOES?: number;
  RECEITA_LIQUIDA?: number;
  CUSTOS?: number;
  LUCRO_BRUTO?: number;
  DESPESAS_OPERACIONAIS?: number;
  EBITDA?: number;
  RESULTADO_FINANCEIRO?: number;
  LUCRO_LIQUIDO?: number;
  [key: string]: any;
}

export const ReceitasDespesasPage: React.FC = () => {
  const { activeWorkspace } = useWorkspace();
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [dreData, setDreData] = useState<DreData | null>(null);
  
  const currentYear = new Date().getFullYear();
  const [selectedYear, setSelectedYear] = useState<number>(currentYear);
  const [selectedMonth, setSelectedMonth] = useState<number | ''>(''); // '' means full year

  const fetchDre = useCallback(async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    try {
      let url = `/workspaces/${activeWorkspace.id}/reports/dre?ano=${selectedYear}`;
      if (selectedMonth !== '') {
        url += `&mes=${selectedMonth}`;
      }
      const response = await api.get(url);
      const data = response.data;
      if (data.dre) {
        setDreData(data.dre);
      } else if (data.acumulado) {
        setDreData(data.acumulado);
      } else {
        setDreData(data);
      }
    } catch (error) {
      console.error('Erro ao buscar DRE:', error);
      setDreData(null);
    } finally {
      setLoading(false);
    }
  }, [activeWorkspace, selectedYear, selectedMonth]);

  useEffect(() => {
    fetchDre();
  }, [fetchDre]);

  const handleExportExcel = async () => {
    if (!activeWorkspace) return;
    setDownloading(true);
    try {
      let url = `/workspaces/${activeWorkspace.id}/reports/dre/download?ano=${selectedYear}`;
      if (selectedMonth !== '') {
        url += `&mes=${selectedMonth}`;
      }
      const response = await api.get(url, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      const monthStr = selectedMonth ? `_${String(selectedMonth).padStart(2, '0')}` : '_anual';
      link.download = `DRE_${activeWorkspace.nome_fantasia || 'Empresa'}_${selectedYear}${monthStr}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Erro ao baixar Excel:', error);
      alert('Erro ao exportar DRE em Excel.');
    } finally {
      setDownloading(false);
    }
  };

  const formatCurrency = (val: number | undefined) => {
    if (val === undefined || val === null) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
  };

  const getDivergenceColor = (val: number | undefined) => {
    if (!val) return 'text-slate-800';
    return val >= 0 ? 'text-emerald-600' : 'text-red-600';
  };

  const months = [
    { value: 1, label: 'Janeiro' },
    { value: 2, label: 'Fevereiro' },
    { value: 3, label: 'Março' },
    { value: 4, label: 'Abril' },
    { value: 5, label: 'Maio' },
    { value: 6, label: 'Junho' },
    { value: 7, label: 'Julho' },
    { value: 8, label: 'Agosto' },
    { value: 9, label: 'Setembro' },
    { value: 10, label: 'Outubro' },
    { value: 11, label: 'Novembro' },
    { value: 12, label: 'Dezembro' },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <Landmark className="w-8 h-8 text-primary-600" />
            DRE Gerencial & Financeiro
          </h1>
          <p className="text-slate-500 mt-1">
            Demonstração do Resultado do Exercício consolidada pelo motor contábil da empresa.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportExcel}
            disabled={downloading || !activeWorkspace}
            className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm px-4 py-2.5 rounded-lg shadow-sm flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            {downloading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            Exportar Excel
          </button>
        </div>
      </div>

      {!activeWorkspace ? (
        <div className="p-12 text-center border border-slate-200 rounded-xl bg-white shadow-sm">
          <AlertCircle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-800 mb-2">Nenhum Workspace Selecionado</h3>
          <p className="text-slate-500">Selecione uma empresa no topo para visualizar a DRE Gerencial.</p>
        </div>
      ) : (
        <>
          {/* Controls / Filter Bar */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Calendar className="w-5 h-5 text-slate-400" />
              <span className="text-sm font-semibold text-slate-700">Período de Análise:</span>
              
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(Number(e.target.value))}
                className="bg-slate-50 border border-slate-300 text-slate-800 rounded-lg text-sm px-3 py-1.5 font-medium outline-none focus:ring-2 focus:ring-primary-500"
              >
                {[currentYear - 2, currentYear - 1, currentYear, currentYear + 1].map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>

              <select
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value === '' ? '' : Number(e.target.value))}
                className="bg-slate-50 border border-slate-300 text-slate-800 rounded-lg text-sm px-3 py-1.5 font-medium outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Acumulado Anual</option>
                {months.map((m) => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))}
              </select>
            </div>

            <button
              onClick={fetchDre}
              disabled={loading}
              className="text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Atualizar
            </button>
          </div>

          {/* Key Metric Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs uppercase font-bold tracking-wider text-slate-400">Receita Bruta</p>
                <h3 className="text-2xl font-bold text-slate-800">{formatCurrency(dreData?.RECEITA_BRUTA)}</h3>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                <DollarSign className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs uppercase font-bold tracking-wider text-slate-400">EBITDA / Operacional</p>
                <h3 className={`text-2xl font-bold ${getDivergenceColor(dreData?.EBITDA)}`}>{formatCurrency(dreData?.EBITDA)}</h3>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                <TrendingDown className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs uppercase font-bold tracking-wider text-slate-400">Resultado Líquido</p>
                <h3 className={`text-2xl font-bold ${getDivergenceColor(dreData?.LUCRO_LIQUIDO)}`}>{formatCurrency(dreData?.LUCRO_LIQUIDO)}</h3>
              </div>
            </div>
          </div>

          {/* Detailed Statement Table */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-800">Demonstrativo Estruturado</h2>
              <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-600 rounded-full border border-slate-200">
                {selectedMonth ? `${months.find(m => m.value === selectedMonth)?.label} / ${selectedYear}` : `Exercício ${selectedYear}`}
              </span>
            </div>

            {loading ? (
              <div className="p-12 text-center text-slate-500 flex flex-col items-center justify-center">
                <RefreshCw className="w-8 h-8 animate-spin text-primary-600 mb-3" />
                Carregando dados financeiros da DRE...
              </div>
            ) : !dreData ? (
              <div className="p-12 text-center text-slate-500">
                Nenhum lançamento contábil processado para o período selecionado.
              </div>
            ) : (
              <div className="divide-y divide-slate-100 text-sm">
                <div className="px-6 py-3.5 flex justify-between items-center bg-slate-50/50 font-bold text-slate-800">
                  <span>(+) RECEITA OPERACIONAL BRUTA</span>
                  <span className="font-mono text-emerald-600">{formatCurrency(dreData.RECEITA_BRUTA)}</span>
                </div>

                <div className="px-6 py-3 flex justify-between items-center text-slate-600 pl-10">
                  <span>(-) Deduções da Receita & Impostos Sobre Vendas</span>
                  <span className="font-mono text-red-500">{formatCurrency(dreData.DEDUCOES)}</span>
                </div>

                <div className="px-6 py-3.5 flex justify-between items-center bg-slate-100/60 font-bold text-slate-900 border-t border-b border-slate-200">
                  <span>(=) RECEITA OPERACIONAL LÍQUIDA</span>
                  <span className="font-mono">{formatCurrency(dreData.RECEITA_LIQUIDA)}</span>
                </div>

                <div className="px-6 py-3 flex justify-between items-center text-slate-600 pl-10">
                  <span>(-) Custo dos Serviços Prestados & Obras (CPV/CSV)</span>
                  <span className="font-mono text-red-500">{formatCurrency(dreData.CUSTOS)}</span>
                </div>

                <div className="px-6 py-3.5 flex justify-between items-center bg-emerald-50/50 font-bold text-slate-900 border-t border-b border-emerald-100">
                  <span>(=) LUCRO BRUTO</span>
                  <span className="font-mono text-emerald-700">{formatCurrency(dreData.LUCRO_BRUTO)}</span>
                </div>

                <div className="px-6 py-3 flex justify-between items-center text-slate-600 pl-10">
                  <span>(-) Despesas Operacionais (Administrativas, Vendas, Gerais)</span>
                  <span className="font-mono text-red-500">{formatCurrency(dreData.DESPESAS_OPERACIONAIS)}</span>
                </div>

                <div className="px-6 py-3.5 flex justify-between items-center bg-indigo-50/50 font-bold text-slate-900 border-t border-b border-indigo-100">
                  <span>(=) EBITDA (RESULTADO OPERACIONAL)</span>
                  <span className="font-mono text-indigo-700">{formatCurrency(dreData.EBITDA)}</span>
                </div>

                <div className="px-6 py-3 flex justify-between items-center text-slate-600 pl-10">
                  <span>(+/-) Resultado Financeiro Líquido</span>
                  <span className="font-mono">{formatCurrency(dreData.RESULTADO_FINANCEIRO)}</span>
                </div>

                <div className="px-6 py-4 flex justify-between items-center bg-slate-900 text-white font-bold text-base rounded-b-xl">
                  <span>(=) RESULTADO LÍQUIDO DO EXERCÍCIO</span>
                  <span className={`font-mono text-lg ${dreData.LUCRO_LIQUIDO && dreData.LUCRO_LIQUIDO >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {formatCurrency(dreData.LUCRO_LIQUIDO)}
                  </span>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};
