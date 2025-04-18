import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface User {
  username: string;
  description: string;
  group: string;
  publicKey: string;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = 'http://3.254.63.138:8050/users/set-up';

  constructor(private http: HttpClient) { }

  createUser(user: User): Observable<any> {
    return this.http.post(this.apiUrl, user);
  }
}
