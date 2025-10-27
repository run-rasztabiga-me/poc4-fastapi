import React, { useState, useEffect } from 'react';
import { Note } from '../App';

interface NoteFormProps {
  note: Note | null;
  onSubmit: (title: string, content: string) => void;
  onCancel: () => void;
}

const NoteForm: React.FC<NoteFormProps> = ({ note, onSubmit, onCancel }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  useEffect(() => {
    if (note) {
      setTitle(note.title);
      setContent(note.content);
    } else {
      setTitle('');
      setContent('');
    }
  }, [note]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim() && content.trim()) {
      onSubmit(title, content);
      if (!note) {
        setTitle('');
        setContent('');
      }
    }
  };

  return (
    <div className="note-form-container">
      <h2>{note ? 'Edytuj notatkę' : 'Dodaj nową notatkę'}</h2>
      <form onSubmit={handleSubmit} className="note-form">
        <div className="form-group">
          <label htmlFor="title">Tytuł:</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Wprowadź tytuł notatki"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="content">Treść:</label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Wprowadź treść notatki"
            rows={5}
            required
          />
        </div>
        <div className="form-actions">
          <button type="submit" className="btn-submit">
            {note ? 'Zaktualizuj' : 'Dodaj'}
          </button>
          {note && (
            <button type="button" onClick={onCancel} className="btn-cancel">
              Anuluj
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default NoteForm;
