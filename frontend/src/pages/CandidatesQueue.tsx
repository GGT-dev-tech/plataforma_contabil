import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { candidatesApi } from '../api/candidates';
import { MatchCandidate } from '../types/candidate';
import { useAuth } from '../auth/AuthProvider';
import { PERMISSIONS, hasPermission } from '../auth/permissions';

export const CandidatesQueue: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [selectedCandidate, setSelectedCandidate] = useState<MatchCandidate | null>(null);
  const [justificativa, setJustificativa] = useState('');
  
  const canApprove = user && hasPermission(user.role, PERMISSIONS.CAN_APPROVE_CANDIDATE);

  const { data: candidates, isLoading, error } = useQuery({
    queryKey: ['candidates', 'PENDENTE_REVISAO'],
    queryFn: candidatesApi.listPending
  });

  const decideMutation = useMutation({
    mutationFn: (args: { id: string, action: 'APROVAR' | 'REJEITAR', comment: string }) => 
      candidatesApi.decide(args.id, args.action, args.comment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
      setSelectedCandidate(null);
      setJustificativa('');
    }
  });

  if (isLoading) return <div style={{ padding: '2rem' }}>Carregando fila de candidatos...</div>;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>Erro ao carregar fila.</div>;
  if (!candidates || candidates.length === 0) return <div style={{ padding: '2rem' }}>A fila de revisão está vazia. Tudo conciliado!</div>;

  return (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Pendentes de Revisão</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* Lista */}
        <div>
          {candidates.map(cand => (
            <div 
              key={cand.id} 
              onClick={() => setSelectedCandidate(cand)}
              style={{
                border: selectedCandidate?.id === cand.id ? '2px solid #2563eb' : '1px solid #d1d5db',
                padding: '1rem',
                borderRadius: '8px',
                marginBottom: '1rem',
                cursor: 'pointer',
                backgroundColor: 'white'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: 'bold' }}>Score: {(cand.score_total * 100).toFixed(0)}%</span>
                <span style={{ color: '#4b5563', fontSize: '0.875rem' }}>{cand.movimentacao_original?.data}</span>
              </div>
              <p style={{ margin: '0', fontSize: '0.875rem', color: '#1f2937' }}>
                <strong>Movimento:</strong> {cand.movimentacao_original?.historico} (R$ {cand.movimentacao_original?.valor})
              </p>
            </div>
          ))}
        </div>

        {/* Detalhe (Explainability) */}
        {selectedCandidate ? (
          <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '8px', border: '1px solid #d1d5db' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>Análise de Decisão (Explainability)</h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ padding: '1rem', backgroundColor: '#f9fafb', borderRadius: '4px' }}>
                <h4 style={{ fontSize: '0.875rem', fontWeight: 'bold', color: '#6b7280', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Dados do Banco</h4>
                <p><strong>Histórico:</strong> {selectedCandidate.movimentacao_original?.historico}</p>
                <p><strong>Valor:</strong> R$ {selectedCandidate.movimentacao_original?.valor}</p>
                <p><strong>Data:</strong> {selectedCandidate.movimentacao_original?.data}</p>
              </div>
              
              <div style={{ padding: '1rem', backgroundColor: '#f9fafb', borderRadius: '4px' }}>
                <h4 style={{ fontSize: '0.875rem', fontWeight: 'bold', color: '#6b7280', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Dados do Sistema (Despesa)</h4>
                <p><strong>Fornecedor:</strong> {selectedCandidate.parcela_original?.fornecedor}</p>
                <p><strong>Documento:</strong> {selectedCandidate.parcela_original?.documento}</p>
                <p><strong>Valor:</strong> R$ {selectedCandidate.parcela_original?.valor}</p>
                <p><strong>Data Vencimento:</strong> {selectedCandidate.parcela_original?.data_vencimento}</p>
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: 'bold', marginBottom: '0.75rem' }}>Regras Aplicadas</h4>
              {selectedCandidate.regras.map((regra, idx) => (
                <div key={idx} style={{ marginBottom: '0.5rem', padding: '0.75rem', borderLeft: regra.score > 0.5 ? '4px solid #10b981' : '4px solid #ef4444', backgroundColor: '#f3f4f6' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                    <span style={{ fontWeight: 'bold' }}>{regra.nome}</span>
                    <span>Score: {regra.score} (Peso: {regra.peso})</span>
                  </div>
                  <p style={{ margin: 0, fontSize: '0.875rem', color: '#4b5563' }}>{regra.justificativa}</p>
                </div>
              ))}
            </div>

            <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '1.5rem' }}>
              <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Justificativa da Revisão</label>
              <textarea 
                rows={3} 
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '4px', marginBottom: '1rem' }}
                value={justificativa}
                onChange={(e) => setJustificativa(e.target.value)}
                placeholder="Insira o motivo se houver dúvida sobre o score..."
                disabled={!canApprove}
              />
              
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button
                  onClick={() => decideMutation.mutate({ id: selectedCandidate.id, action: 'APROVAR', comment: justificativa })}
                  disabled={!canApprove || decideMutation.isPending}
                  title={!canApprove ? "Apenas analistas e administradores podem aprovar" : ""}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    backgroundColor: canApprove ? '#16a34a' : '#9ca3af',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontWeight: 'bold',
                    cursor: canApprove ? 'pointer' : 'not-allowed'
                  }}
                >
                  {decideMutation.isPending ? 'Processando...' : 'Aprovar Conciliação'}
                </button>
                <button
                  onClick={() => decideMutation.mutate({ id: selectedCandidate.id, action: 'REJEITAR', comment: justificativa })}
                  disabled={!canApprove || decideMutation.isPending}
                  title={!canApprove ? "Apenas analistas e administradores podem rejeitar" : ""}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    backgroundColor: canApprove ? '#dc2626' : '#9ca3af',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontWeight: 'bold',
                    cursor: canApprove ? 'pointer' : 'not-allowed'
                  }}
                >
                  {decideMutation.isPending ? 'Processando...' : 'Rejeitar'}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f9fafb', border: '2px dashed #d1d5db', borderRadius: '8px' }}>
            <p style={{ color: '#6b7280' }}>Selecione um candidato para visualizar os detalhes.</p>
          </div>
        )}
      </div>
    </div>
  );
};
