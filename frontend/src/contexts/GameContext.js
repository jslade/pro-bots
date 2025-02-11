import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';

import { ApiContext } from './ApiContext';
import { SessionContext } from './SessionContext';

const GameContext = createContext();

const GameProvider = ({ children }) => {
    const session = useContext(SessionContext);
    const api = useContext(ApiContext);

    const [ gameStateRequested, setGameStateRequested] = useState(false)
    const [ addPlayerRequested, setAddPlayerRequested] = useState(false)

    const [ gameState, setGameState ] = useState(null)
    const [ player, setPlayer ] = useState(null)
    const [ probot, setProbot ] = useState(null)

    const handleGameStateReset = useCallback((data) => {
        setGameState(data.current);
    }, [setGameState])

    const handleGameStateCurrent = useCallback((data) => {
        setGameState(data);
    }, [setGameState])

    useEffect(() => {
        if (!api) return;

        api.registerCallback('game', 'reset', (data) => {
            handleGameStateReset(data);
        });
        api.registerCallback('game', 'current_state', (data) => {
            handleGameStateCurrent(data);
        });
    }, [api, api?.registerCallback, handleGameStateCurrent, handleGameStateReset]);

    const requestGameState = useCallback(() => {
        if (!api || gameStateRequested) return;

        console.log("Requesting current game state");
        setGameStateRequested(true);
        api.sendMessage("game", "get_current");
    }, [api, gameStateRequested, setGameStateRequested])

    const requestAddPlayer = useCallback(() => {
        if (!api || !session?.isPlayer || addPlayerRequested) return;

        console.log("Requesting a new Player for me");
        setAddPlayerRequested(true);
        api.sendMessage("game", "add_player", { sessionId: session.sessionId })
    }, [api, addPlayerRequested, setAddPlayerRequested,
        session?.isPlayer, session?.sessionId]);

    useEffect(() => {
        if (!session?.connected) {
            setGameStateRequested(false);
        };

        if (!gameState && !gameStateRequested) {
            requestGameState();
        }

    }, [requestGameState, gameStateRequested, gameState, session?.connected]);


    useEffect(() => {
        if (!api || !gameState) return;

        console.log("Setting new gameState", gameState);

        for(const existing_player of gameState.players) {
            let found = false;
            if (existing_player.sessionId === session.sessionId) {
                console.log("Got player for me", existing_player);
                setPlayer(existing_player);
                found = true;

                for(const existing_probot of gameState.probots) {
                    if (existing_probot.player === existing_player.name) {
                        console.log("Got probot for me", existing_probot);
                        setProbot(existing_probot);
                    }
                }
            }
            if (!found) {
                requestAddPlayer();
            }

        }

    }, [api, gameState,
        player, setPlayer,
        probot, setProbot,
        requestAddPlayer,
        session?.sessionId])

    return (
        <GameContext.Provider value={{
            gameState,
            player,
            probot,
        }}>
            {children}
        </GameContext.Provider>
    );
};

export { GameContext, GameProvider };