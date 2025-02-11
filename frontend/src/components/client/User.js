import React, { useContext } from 'react';
import Login from './Login';
import Workspace from './workspace/Workspace';
import { SessionContext } from '../../contexts/SessionContext';

const User = () => {
    const session = useContext(SessionContext);

    return (
        <div>
            {session.sessionId ? <Workspace /> : <Login />}
        </div>
    );
};

export default User;
