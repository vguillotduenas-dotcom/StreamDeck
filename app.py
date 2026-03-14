if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(is_admin=True).first():
            db.session.add(User(password='ADMIN123', is_admin=True))
            db.session.commit()
    
    # C'EST CETTE LIGNE QUI CHANGE TOUT :
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
