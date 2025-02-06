import React, { createContext } from 'react';

import {
    QueryClient,
    QueryClientProvider,
} from '@tanstack/react-query'
  
  
import API from '../api'

const queryClient = new QueryClient()
const api = new API();

const ApiContext = createContext();

const ApiProvider = ({ children }) => {
    return (
        <ApiContext.Provider value={api}>
            <QueryClientProvider client={queryClient}>
                {children}
            </QueryClientProvider>
        </ApiContext.Provider>
    );
};

export { ApiContext, ApiProvider };
