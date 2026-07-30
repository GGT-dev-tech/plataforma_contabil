import { test, expect } from '@playwright/test';

test.describe('Cenário Auditor', () => {
  test('Auditor não pode aprovar', async ({ page }) => {
    // 1. Login
    await page.goto('/login');
    await page.fill('input[type="email"]', 'auditor@contabil.com');
    await page.fill('input[type="password"]', 'auditor123');
    await page.click('button[type="submit"]');

    // 2. Tenta ir direto para Criar Execução (bloqueado)
    await page.goto('/executions/new');
    await expect(page.locator('text=Acesso Negado')).toBeVisible();

    // 3. Fila de candidatos
    await page.goto('/candidates');
    
    const isVazia = await page.locator('text=A fila de revisão está vazia').isVisible();
    if (!isVazia) {
      await page.locator('div[style*="cursor: pointer"]').first().click();
      
      // O botão aprovar tem que estar disabled
      const btnAprovar = page.locator('button:has-text("Aprovar Conciliação")');
      await expect(btnAprovar).toBeDisabled();
    }
  });
});
