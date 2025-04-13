import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { UserService, User } from '../../services/user.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './user-management.component.html',
  styleUrls: ['./user-management.component.scss']
})
export class UserManagementComponent {
  userForm: FormGroup;
  groups = ['developer', 'devops', 'tester'];
  errorMessage: string = '';
  successMessage: string = '';

  constructor(
    private readonly fb: FormBuilder,
    private readonly userService: UserService
  ) {
    this.userForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      description: ['', Validators.required],
      group: ['', Validators.required],
      publicKey: ['', [Validators.required, this.validateSshKey]]
    });
  }

  validateSshKey(control: any) {
    const sshKeyPattern = /^ssh-rsa AAAA[0-9A-Za-z+/]+[=]{0,3}( [^@]+@[^@]+)?$/;
    if (control.value && !sshKeyPattern.test(control.value)) {
      return { invalidSshKey: true };
    }
    return null;
  }

  onSubmit() {
    if (this.userForm.valid) {
      const userData: User = this.userForm.value;
      this.userService.createUser(userData).subscribe({
        next: () => {
          this.successMessage = 'User created successfully!';
          this.errorMessage = '';
          this.userForm.reset();
        },
        error: (error) => {
          this.errorMessage = 'Error creating user: ' + error.message;
          this.successMessage = '';
        }
      });
    }
  }
}
