import React, { createContext, useState } from 'react';

// Create the context
const SessionContext = createContext();

// Create a provider component
const SessionProvider = ({ children }) => {
    const [sessionId, setSessionId] = useState(null);

    return (
        <SessionContext.Provider value={{
            sessionId, setSessionId,
        }}>
            {children}
        </SessionContext.Provider>
    );
};

export { SessionContext, SessionProvider };