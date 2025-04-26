/**
 * Exportação de todos os serviços disponíveis
 */

import RelatoriosService from './RelatoriosService';
import AuthService from './AuthService';
import DatabaseService from './DatabaseService';
import ApiService from './ApiService';

export {
  RelatoriosService,
  AuthService,
  DatabaseService,
  ApiService
};

// Exportação padrão para facilitar importações
export default {
  RelatoriosService,
  AuthService,
  DatabaseService,
  ApiService
};