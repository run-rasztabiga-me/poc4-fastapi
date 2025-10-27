import React from 'react';
import { Note } from '../App';

interface NotesListProps {
  notes: Note[];
  onEdit: (note: Note) => void;
  onDelete: (id: number) => void;
}

const NotesList: React.FC<NotesListProps> = ({ notes, onEdit, onDelete }) => {
  if (notes.length === 0) {
    return <div className="no-notes">Brak notatek. Utwórz swoją pierwszą notatkę!</div>;
  }

  return (
    <div className="notes-list">
      {notes.map((note) => (
        <div key={note.id} className="note-card">
          <h3>{note.title}</h3>
          <p>{note.content}</p>
          <div className="note-meta">
            <small>Utworzono: {new Date(note.created_at).toLocaleString('pl-PL')}</small>
          </div>
          <div className="note-actions">
            <button onClick={() => onEdit(note)} className="btn-edit">
              Edytuj
            </button>
            <button onClick={() => onDelete(note.id)} className="btn-delete">
              Usuń
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default NotesList;
