import React from 'react';
import User from './User';
import { SessionProvider } from './SessionContext';

const Client = () => {
    return (
        <SessionProvider>
            <User />
        </SessionProvider>
    );
};

export default Client;
