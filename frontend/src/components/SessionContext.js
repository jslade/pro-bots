import React, { createContext, useState } from 'react';

// Create the context
const SessionContext = createContext();

// Create a provider component
const SessionProvider = ({ children }) => {
    const [sessionId, setSessionId] = useState(null);
    const [connected, setConnected] = useState(false);

    // Move to user:
    //const [name, setName] = useState(null);
    //const [program, setProgram] = useState('');

    return (
        <SessionContext.Provider value={{
            sessionId, setSessionId,
            connected, setConnected,
        }}>
            {children}
        </SessionContext.Provider>
    );
};

export { SessionContext, SessionProvider };