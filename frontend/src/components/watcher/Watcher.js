import React from 'react';
import { useContext, useEffect } from 'react';

import { SessionContext } from '../../contexts/SessionContext';
import { ApiProvider } from '../../contexts/ApiContext';
import { GameProvider } from '../../contexts/GameContext';

import WatcherLayout from './WatcherLayout';

function generateServerSessionId() {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    let result = 'watch-';
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
            session.setIsPlayer(false);
        }
    }, [session, session.sessionId, session.setSessionId]);

    return (
        <ApiProvider>
            <GameProvider>
                <WatcherLayout />
            </GameProvider>
        </ApiProvider>
    );
}

export default Watcher;