"""Application routes."""
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from app.services import ritual_service, log_service, summary_service, reflection_service, auth_service


def register_routes(app):
    """Register all routes with the Flask app."""
    
    # =========================================================================
    # HOME
    # =========================================================================
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # =========================================================================
    # AUTHENTICATION
    # =========================================================================
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')
            
            errors = auth_service.validate_registration_data(username, password, password_confirm)
            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(url_for('register'))
            
            exists, error_msg = auth_service.check_user_exists(username)
            if exists:
                flash(error_msg, 'error')
                return redirect(url_for('register'))
            
            auth_service.create_user(username, password)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember = request.form.get('remember', False)
            
            user, error_msg = auth_service.authenticate_user(username, password)
            
            if error_msg:
                flash(error_msg, 'error')
                return redirect(url_for('login'))
            
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('index'))
    
    # =========================================================================
    # RITUAL LOGGING
    # =========================================================================
    
    @app.route('/rituals', methods=['GET', 'POST'])
    @login_required
    def rituals():
        if request.method == 'POST':
            ritual_id = request.form.get('ritual_id')
            context = request.form.get('context')
            reflection = request.form.get('reflection', '').strip()
            
            if not ritual_id:
                flash('Please select a ritual.', 'error')
                return redirect(url_for('rituals'))
            
            if not reflection:
                flash('Please provide a reflection.', 'error')
                return redirect(url_for('rituals'))
            
            log_service.create_log_entry(
                user_id=current_user.id,
                ritual_id=int(ritual_id),
                context=context,
                reflection=reflection
            )
            
            flash('Ritual logged successfully!', 'success')
            return redirect(url_for('rituals'))
        
        page = request.args.get('page', 1, type=int)
        available_rituals = ritual_service.get_available_rituals(current_user.id)
        pagination = log_service.get_user_ritual_logs_paginated(current_user.id, page=page, per_page=10)
        
        return render_template('rituals.html', 
                             available_rituals=available_rituals,
                             ritual_entries=pagination.items,
                             pagination=pagination)
    
    @app.route('/rituals/edit/<int:entry_id>', methods=['GET', 'POST'])
    @login_required
    def edit_log_entry(entry_id):
        entry = log_service.get_log_entry_by_id(entry_id)
        
        if not entry:
            flash('Log entry not found.', 'error')
            return redirect(url_for('rituals'))
        
        if not log_service.can_user_modify_log(entry, current_user.id):
            flash('You can only edit your own ritual logs.', 'error')
            return redirect(url_for('rituals'))
        
        if request.method == 'POST':
            ritual_id = request.form.get('ritual_id')
            context = request.form.get('context')
            reflection = request.form.get('reflection', '').strip()
            
            if not ritual_id:
                flash('Please select a ritual.', 'error')
                return redirect(url_for('edit_log_entry', entry_id=entry_id))
            
            if not reflection:
                flash('Please provide a reflection.', 'error')
                return redirect(url_for('edit_log_entry', entry_id=entry_id))
            
            log_service.update_log_entry(
                entry=entry,
                ritual_id=int(ritual_id),
                context=context,
                reflection=reflection
            )
            
            flash('Ritual log updated successfully!', 'success')
            return redirect(url_for('rituals'))
        
        available_rituals = ritual_service.get_available_rituals(current_user.id)
        return render_template('edit_log_entry.html', entry=entry, available_rituals=available_rituals)
    
    @app.route('/rituals/delete/<int:entry_id>', methods=['POST'])
    @login_required
    def delete_log_entry(entry_id):
        entry = log_service.get_log_entry_by_id(entry_id)
        
        if not entry:
            flash('Log entry not found.', 'error')
            return redirect(url_for('rituals'))
        
        if not log_service.can_user_modify_log(entry, current_user.id):
            flash('You can only delete your own ritual logs.', 'error')
            return redirect(url_for('rituals'))
        
        log_service.delete_log_entry(entry)
        flash('Ritual log deleted successfully.', 'success')
        return redirect(url_for('rituals'))
    
    # =========================================================================
    # MY RITUALS
    # =========================================================================
    
    @app.route('/my-rituals')
    @login_required
    def my_rituals():
        preset_rituals = ritual_service.get_preset_rituals()
        custom_rituals = ritual_service.get_user_custom_rituals(current_user.id)
        return render_template('my_rituals.html',
                             preset_rituals=preset_rituals,
                             custom_rituals=custom_rituals)
    
    @app.route('/my-rituals/create', methods=['GET', 'POST'])
    @login_required
    def create_ritual():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            primary_category = request.form.get('primary_category', '').strip()
            secondary_category = request.form.get('secondary_category', '').strip()
            source = request.form.get('source', '').strip()
            redirect_to = request.form.get('redirect_to', '')
            
            if not name:
                flash('Ritual name is required.', 'error')
                if redirect_to == 'rituals':
                    return redirect(url_for('rituals'))
                return redirect(url_for('create_ritual'))
            
            ritual = ritual_service.create_custom_ritual(
                user_id=current_user.id,
                name=name,
                description=description or None,
                primary_category=primary_category or None,
                secondary_category=secondary_category or None,
                source=source or None
            )
            
            flash(f'Custom ritual "{ritual.name}" created successfully!', 'success')
            
            if redirect_to == 'rituals':
                return redirect(url_for('rituals'))
            return redirect(url_for('my_rituals'))
        
        return render_template('ritual_form.html', ritual=None, action='Create')
    
    @app.route('/my-rituals/edit/<int:ritual_id>', methods=['GET', 'POST'])
    @login_required
    def edit_ritual(ritual_id):
        ritual = ritual_service.get_ritual_by_id(ritual_id)
        
        if not ritual:
            flash('Ritual not found.', 'error')
            return redirect(url_for('my_rituals'))
        
        if not ritual_service.can_user_modify_ritual(ritual, current_user.id):
            flash('You can only edit your own custom rituals.', 'error')
            return redirect(url_for('my_rituals'))
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            primary_category = request.form.get('primary_category', '').strip()
            secondary_category = request.form.get('secondary_category', '').strip()
            source = request.form.get('source', '').strip()
            
            if not name:
                flash('Ritual name is required.', 'error')
                return redirect(url_for('edit_ritual', ritual_id=ritual_id))
            
            ritual = ritual_service.update_custom_ritual(
                ritual=ritual,
                name=name,
                description=description or None,
                primary_category=primary_category or None,
                secondary_category=secondary_category or None,
                source=source or None
            )
            
            flash(f'Ritual "{ritual.name}" updated successfully!', 'success')
            return redirect(url_for('my_rituals'))
        
        return render_template('ritual_form.html', ritual=ritual, action='Edit')
    
    @app.route('/my-rituals/delete/<int:ritual_id>', methods=['POST'])
    @login_required
    def delete_ritual(ritual_id):
        ritual = ritual_service.get_ritual_by_id(ritual_id)
        
        if not ritual:
            flash('Ritual not found.', 'error')
            return redirect(url_for('my_rituals'))
        
        if not ritual_service.can_user_modify_ritual(ritual, current_user.id):
            flash('You can only delete your own custom rituals.', 'error')
            return redirect(url_for('my_rituals'))
        
        ritual_name = ritual.name
        success = ritual_service.delete_custom_ritual(ritual)
        
        if success:
            flash(f'Ritual "{ritual_name}" deleted successfully.', 'success')
        else:
            flash(f'Cannot delete "{ritual_name}" because it has been used in ritual log(s).', 'error')
        
        return redirect(url_for('my_rituals'))
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    
    @app.route('/summary', methods=['GET', 'POST'])
    @login_required
    def summary():
        from datetime import timedelta
        week_start, _ = summary_service.get_week_date_range()
        
        if request.method == 'POST':
            reflection_text = request.form.get('reflection', '').strip()
            
            if reflection_text:
                reflection_service.create_reflection(
                    user_id=current_user.id,
                    reflection_text=reflection_text
                )
                flash('Reflection saved!', 'success')
            else:
                flash('Please enter a reflection before saving.', 'error')
            
            return redirect(url_for('summary'))
        
        virtue_metrics = summary_service.calculate_virtue_metrics(current_user.id)
        total_rituals = summary_service.get_total_rituals_this_week(current_user.id)
        last_week_total = summary_service.get_total_rituals_last_week(current_user.id)
        week_change = total_rituals - last_week_total
        days_practiced = summary_service.get_days_practiced_this_week(current_user.id)
        streak = summary_service.calculate_current_streak(current_user.id)
        all_time = summary_service.get_all_time_stats(current_user.id)
        weekly_trend = summary_service.get_weekly_trend(current_user.id)
        
        page = request.args.get('page', 1, type=int)
        reflection_pagination = reflection_service.get_user_reflections_paginated(
            current_user.id, page=page, per_page=10
        )
        
        return render_template('summary.html',
                             virtue_metrics=virtue_metrics,
                             total_rituals=total_rituals,
                             week_change=week_change,
                             days_practiced=days_practiced,
                             streak=streak,
                             week_start=week_start,
                             timedelta=timedelta,
                             all_time=all_time,
                             weekly_trend=weekly_trend,
                             reflections=reflection_pagination.items,
                             reflection_pagination=reflection_pagination)
    
    # =========================================================================
    # USER PROFILE
    # =========================================================================
    
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'change_password':
                current_password = request.form.get('current_password', '')
                new_password = request.form.get('new_password', '')
                confirm_password = request.form.get('confirm_password', '')
                
                if not current_user.check_password(current_password):
                    flash('Current password is incorrect.', 'error')
                    return redirect(url_for('profile'))
                
                if len(new_password) < 6:
                    flash('New password must be at least 6 characters long.', 'error')
                    return redirect(url_for('profile'))
                
                if new_password != confirm_password:
                    flash('New passwords do not match.', 'error')
                    return redirect(url_for('profile'))
                
                current_user.set_password(new_password)
                from app import db
                db.session.commit()
                
                flash('Password changed successfully!', 'success')
                return redirect(url_for('profile'))
        
        stats = {'streak': summary_service.calculate_current_streak(current_user.id)}
        return render_template('profile.html', stats=stats)
