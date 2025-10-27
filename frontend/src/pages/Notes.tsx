import React from 'react';
import NoteForm from '../components/NoteForm';
import NotesList from '../components/NotesList';
import { Note } from '../App';

interface NotesProps {
  notes: Note[];
  editingNote: Note | null;
  loading: boolean;
  onCreateNote: (title: string, content: string) => Promise<void>;
  onUpdateNote: (id: number, title: string, content: string) => Promise<void>;
  onDeleteNote: (id: number) => Promise<void>;
  setEditingNote: (note: Note | null) => void;
}

const Notes: React.FC<NotesProps> = ({
  notes,
  editingNote,
  loading,
  onCreateNote,
  onUpdateNote,
  onDeleteNote,
  setEditingNote,
}) => {
  return (
    <>
      <NoteForm
        note={editingNote}
        onSubmit={(title, content) => {
          if (editingNote) {
            onUpdateNote(editingNote.id, title, content);
          } else {
            onCreateNote(title, content);
          }
        }}
        onCancel={() => setEditingNote(null)}
      />

      {loading ? (
        <p>Loading notes...</p>
      ) : (
        <NotesList
          notes={notes}
          onEdit={setEditingNote}
          onDelete={onDeleteNote}
        />
      )}
    </>
  );
};

export default Notes;
