import React from 'react';
import { useContext, useEffect } from 'react';
import { SessionContext } from '../../contexts/SessionContext';

function generateServerSessionId() {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    let result = 'srv-';
    for (let i = 0; i < 5; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}

function Watcher() {
    const session = useContext(SessionContext);

    useEffect(() => {
        if (!session.sessionId) {
            const newSessionId = generateServerSessionId();
            session.setSessionId(newSessionId);
        }
    }, [session, session.sessionId, session.setSessionId]);

    return (
        <div>
            This is the watcher view
        </div>
    );
}

export default Watcher;