import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { UserManagementComponent } from './components/user-management/user-management.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule, UserManagementComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'User Management';
}
