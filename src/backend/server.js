
// Servidor principal para o Sistema de Protesto
import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import remessasRoutes from './routes/remessas.js';

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Middleware para autenticação (simplificado)
app.use((req, res, next) => {
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    // Aqui você implementaria a verificação do token
    // Por simplicidade, apenas simulamos um usuário autenticado
    req.user = { id: 1, username: 'usuario_teste', admin: true };
  }
  next();
});

// Rotas
app.use('/remessas', remessasRoutes);

// Rota para desistências (redirecionando para o controlador de remessas)
app.use('/desistencias', (req, res, next) => {
  req.originalUrl = req.originalUrl.replace('/desistencias', '/remessas/desistencias');
  req.url = req.url.replace('/desistencias', '/remessas/desistencias');
  next();
}, remessasRoutes);

// Rota de teste
app.get('/', (req, res) => {
  res.json({ message: 'API do Sistema de Protesto funcionando!' });
});

// Tratamento de erros
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    message: 'Ocorreu um erro no servidor',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// Iniciar o servidor
app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});

export default app;